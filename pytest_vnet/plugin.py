#!/usr/bin/env python3

import os
import re
import sys
import shutil
import pathlib
import inspect

import pytest
import docker

from typing import Optional, Tuple, Union, List
from tempfile import TemporaryDirectory

from docker.types import Mount
from docker.errors import DockerException
from docker.models.containers import Container

PYTHON_VERSION = f"{sys.version_info[0]}."\
    f"{sys.version_info[1]}."\
    f"{sys.version_info[2]}"


run_in_netvm = pytest.mark.run_in_netvm


class NonZeroExitcode(Exception):
    ...


class DockerInitError(Exception):
    ...


class VNetItem:

    def __init__(self, plugin, item):
        self.plugin = plugin
        self.item = item
        self.dir = TemporaryDirectory()

    def prepare_run(self):
        code_str = inspect.getsource(self.item.function)
        src_lines = code_str.split('\n')[2:]
        test_code = "\n".join(src_lines)

        with open(f"{self.dir.name}/test.py", "w+") as test_script:
            test_script.write("import sys\n")
            test_script.write("import logging\n")
            test_script.write("import traceback\n")
            for path in self.plugin.sys_path_targets:
                test_script.write(f"sys.path.append(\"{path}\")\n")

            # To disable resource limit error message in mininet
            test_script.write("from mininet.net import Mininet\n")
            test_script.write("from mininet.node import Controller\n")
            test_script.write("from mininet.log import setLogLevel\n")
            test_script.write("setLogLevel(\"critical\")\n")

            # Additial tools inside vm scripts
            test_script.write("from pytest_vnet import as_script, as_host\n")


            test_script.write("vnet = Mininet(controller=Controller)\n")
            test_script.write("try:\n")
            test_script.write("    vnet.addController('c0')\n")
            test_script.write(test_code)
            test_script.write("except Exception as e:\n")
            test_script.write("    sys.stderr.write(traceback.format_exc())\n")
            test_script.write("\nvnet.stop()\n")

        self.fspath = f"{self.dir.name}/test.py"
        self.mount = Mount(
            f"/root/tests/{self.dir.name[5:]}",
            self.dir.name,
            "bind"
            )
        self.plugin.dynmounts.append(self.mount)

    def runtest(self):
        ec, stdouts = self.plugin.container.exec_run(
            ["python3", "test.py"],
            workdir=f"/root/tests/{self.dir.name[5:]}/",
            demux=True
        )

        stdout, stderr = stdouts

        if stdout is not None:
            tot_stdout = stdout.decode("utf-8")

            print(tot_stdout)

        if stderr is not None:
            tot_stderr = stderr.decode("utf-8")
            raise AssertionError(tot_stderr)

    def cleanup(self):
        self.dir.cleanup()


class VirtualNetworkPlugin:

    def __init__(self, items):
        self.dynmounts: List[Mount] = []
        self.sys_path_targets: List[str] = []
        self.container: Optional[Container] = None
        self.vm_items: List[Item] = [
            VNetItem(self, item) for item in items if item.get_closest_marker("run_in_netvm")
        ]

        self.vm_required: bool = len(self.vm_items) > 0

        if not self.vm_required:
            return

        try:
            self.docker_client = docker.from_env()

        except DockerException as e:
            raise DockerInitError(f"Is docker running?: \n{e}")

        # Read current sys.path, and create future bind mounts to container /root/lib
        for source_path in sys.path:

            # Append  /root/python_env to all found paths
            target_path = f"/root/python_env{source_path}"

            # If path exists create, read only bind mount
            if pathlib.Path(source_path).exists():
                self.sys_path_targets.append(target_path)
                self.dynmounts.append(
                    Mount(
                        target_path,
                        source_path,
                        "bind",
                        read_only=True
                    )
                )

        for item in self.vm_items:
            item.prepare_run()

    def exec_in_vm(self, *args, display=True, **kwargs) -> Tuple[int, str]:
        """Run and if a non zero exit code is returned raise exception
        """
        if display:
            print(" ".join(args[0]), end=" ... ", flush=True)
        ec, out = self.container.exec_run(
            *args, **kwargs
        )
        if ec != 0:
            if display:
                print(f"exception!\nec: {ec}\n{out}")
            raise NonZeroExitcode(ec)
        if display:
            print("done")

        return ec, out.decode("utf-8")


    def init_python(self, target_version: Optional[str] = None) -> None:
        if target_version is None:
            target_version = PYTHON_VERSION

        print("instantiating container", end=" ... ", flush=True)
        self.container = self.docker_client.containers.create(
            "guilledk/pytest-vnet:netvm",
            privileged=True,
            tty=True,
            mounts=self.dynmounts
        )

        self.container.start()
        print("done")

        try:
            """Get a copy of the source of the currently running python version
            and untar it.
            """
            self.exec_in_vm(
                ["curl", "-O", f"https://www.python.org/ftp/python/{target_version}/Python-{target_version}.tar.xz"],
                workdir="/root"
            )
            self.exec_in_vm(
                ["tar", "-xf", f"Python-{target_version}.tar.xz"],
                workdir="/root"
            )

            # Configure, Compile & Install
            self.exec_in_vm(
                ["./configure"],
                workdir=f"/root/Python-{target_version}"
            )
            self.exec_in_vm(
                ["make", "-j", str(os.cpu_count())],
                workdir=f"/root/Python-{target_version}"
            )
            self.exec_in_vm(
                ["make", "install"],
                workdir=f"/root/Python-{target_version}"
            )

            # Install mininet python package
            self.exec_in_vm(
                ["pip3", "install", "."],
                workdir=f"/home/mininet"
            )

        except NonZeroExitcode as ex:
            self.container.stop()
            self.container.remove()
            raise

        else:
            # Save the image
            self.container.commit(f"pytest-vnet:netvm-{target_version}")

        print(f"container pytest-vnet:netvm-{target_version} ready.")

    def init_container(self):
        # Check if base image is present or pull it
        try:
            netvm_base_image = self.docker_client.images.get("guilledk/pytest-vnet:netvm")
            print()

        except docker.errors.ImageNotFound:
            print("\nbase netvm image not found, pulling 242mb", end=" ... ", flush=True)
            self.docker_client.images.pull("guilledk/pytest-vnet", "netvm")
            print("done")

        print("starting netvm", end=" ... ", flush=True)
        # Check if python enabled version is present or create it           
        try:

            # Instance container
            self.container = self.docker_client.containers.create(
                f"pytest-vnet:netvm-{PYTHON_VERSION}",
                privileged=True,
                tty=True,
                mounts=self.dynmounts
            )
            self.container.start()
            print("done")

        except docker.errors.ImageNotFound:
            print(
                f"installing python {PYTHON_VERSION}",
                end=" ... ", flush=True
            )
            self.init_python()

        self.exec_in_vm(["service", "openvswitch-switch", "start"])
        self.exec_in_vm(["ovs-vsctl", "set-manager", "ptcp:6640"])

    def shutdown(self):
        if self.container:
            print("\n\nstopping netvm", end=" ... ", flush=True)
            self.container.stop()
            self.container.remove()
            print("done")

        # Delete tmp dirs
        for vmitem in self.vm_items:
            vmitem.cleanup()


VNET_PLUGIN: Optional[VirtualNetworkPlugin] = None


def pytest_addoption(parser):
    parser.addoption(
        "--disable-vnet",
        action="store_true",
        default=False,
        help="Disable virtual network tests.",
    )


def pytest_runtest_setup(item):
    if item.get_closest_marker("run_in_netvm"):
        if item.config.getoption("--disable-vnet"):
            pytest.skip("vnet tests were disabled")


def pytest_collection_modifyitems(session, config, items):

    if config.getoption("--disable-vnet"):
        return

    global VNET_PLUGIN

    VNET_PLUGIN = VirtualNetworkPlugin(items)

    if VNET_PLUGIN.vm_required:
        VNET_PLUGIN.init_container()


def pytest_sessionfinish(session, exitstatus):
    global VNET_PLUGIN

    if VNET_PLUGIN and VNET_PLUGIN.vm_required:
        VNET_PLUGIN.shutdown()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    global VNET_PLUGIN

    if VNET_PLUGIN is not None:
        item_search = [
            vmitem for vmitem in VNET_PLUGIN.vm_items if vmitem.item == item
        ]

        if len(item_search) > 0:
            vmitem = item_search[0]
            item.obj = vmitem.runtest

    yield


def as_script(func):

    import inspect

    with open(
        f"/root/scripts/{func.__name__}.py", 'w+'
    ) as source_file:
        code_str = inspect.getsource(func)
        src_lines = code_str.split('\n')[2:]

        if src_lines[0][0] == '\t':
            func_code = "\n".join([line[1:] for line in src_lines])
        elif src_lines[0][0] == ' ':
            for i, ch in enumerate(src_lines[0]):
                if ch != ' ':
                    func_code = "\n".join([line[i:] for line in src_lines])
                    break
        else:
            raise IndentationError(f"In function {func.__name__}")

        source_file.write("import sys\n")
        for path in sys.path:
            source_file.write(f"sys.path.append(\"{path}\")\n")
        source_file.write(func_code)

    def direct_call(*args, **kwargs):
        direct_call(*args, **kwargs)

    direct_call.path = f"/root/scripts/{func.__name__}.py"

    return direct_call


def as_host(vnet, hostname, addr, link):

    def wrapper(func):
        func = as_script(func)
        func.host = vnet.addHost(hostname, ip=addr)
        vnet.addLink(func.host, link)
        def _start_proc():
            func.proc = func.host.popen(["python3", func.path])
        func.start_host = _start_proc
        return func

    return wrapper