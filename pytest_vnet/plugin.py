#!/usr/bin/env python3

import re
import sys
import pytest
import docker
import pathlib

from typing import Optional

from docker.types import Mount
from docker.models.containers import Container


PYTHON_VERSION = f"{sys.version_info[0]}."\
    f"{sys.version_info[1]}."\
    f"{sys.version_info[2]}"


run_in_netvm = pytest.mark.run_in_netvm


class NonZeroExitcode(Exception):
    ...


class VirtualNetworkPlugin:

    def __init__(self, items):
        self.container: Optional[Container] = None
        self.vm_items: List[Item] = [
            item for item in items if item.get_closest_marker("run_in_netvm")
        ]

        self.vm_required: bool = len(self.vm_items) > 0

        if not self.vm_required:
            return

        self.docker_client = docker.from_env()

        # Read current sys.path, and create future bind mounts to container /root/lib
        self.dynmounts: List[Mount] = []
        self.sys_path_targets: List[str] = []

        for source_path in sys.path:

            # Replace all whats in front of "lib/python" in paths with /root
            search = re.search("lib/python", source_path)
            if search:
                start_idx = search.start()
                target_path = f"/root/{source_path[start_idx:]}"

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

    def exec_in_vm(self, *args, **kwargs) -> int:
        """Run and if a non zero exit code is returned raise exception
        """
        print(" ".join(args[0]), end=" ... ", flush=True)
        ec, _ = self.container.exec_run(
            *args, **kwargs
        )
        if ec != 0:
            print("exception!")
            raise NonZeroExitcode(
                f"Command \"{args[0]}\" returned non zero exitcode {ec}."
            )
        print("done")
        return ec

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
                ["make", "-j", "2"],
                workdir=f"/root/Python-{target_version}"
            )
            self.exec_in_vm(
                ["make", "install"],
                workdir=f"/root/Python-{target_version}"
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

        except docker.errors.ImageNotFound:
            print("\nbase netvm image not found, pulling 238.3mb", end=" ... ", flush=True)
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

        except docker.errors.ImageNotFound:
            print(
                f"installing python {PYTHON_VERSION}",
                end=" ... ", flush=True
            )
            self.init_python()

        # Restart openvswitch just in case
        self.exec_in_vm(["service", "openvswitch-switch", "restart"])

    def shutdown(self):
        if self.container is not None:
            self.container.stop()
            self.container.remove()