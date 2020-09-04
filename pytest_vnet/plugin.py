#!/usr/bin/env python3
import sys
import subprocess

from typing import Optional
from tempfile import NamedTemporaryFile

import pytest
import docker

from mininet.net import Mininet
from mininet.node import Controller

from .vm import VirtualNetworkPlugin


VNET_PLUGIN: Optional[VirtualNetworkPlugin] = None

multihost_test = pytest.mark.multihost

def pytest_addoption(parser):
    parser.addoption(
        "--enable-netvm",
        action="store_true",
        default=False,
        help="Enable container for run_in_netvm marked tests.",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "run_in_netvm: mark test to run inside a container"
    )


def pytest_runtest_setup(item):
    if not item.config.getoption("--enable-netvm"):
        if item.get_closest_marker("run_in_netvm"):
            pytest.skip("netvm tests were disabled")


def pytest_collection_modifyitems(session, config, items):

    if not config.getoption("--enable-netvm"):
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

    import os
    import random
    import inspect

    # create source code
    code_str = inspect.getsource(func)
    src_lines = code_str.split('\n')

    # remove function signature
    i = 0
    while f"def {func.__name__}(" not in src_lines[i]:
        i += 1
    src_lines = src_lines[i+1:]

    if src_lines[0][0] == '\t':
        for i, ch in enumerate(src_lines[0]):
            if ch != '\t':
                src_lines = [line[i:] for line in src_lines]
                break

    elif src_lines[0][0] == ' ':
        for i, ch in enumerate(src_lines[0]):
            if ch != ' ':
                src_lines = [line[i:] for line in src_lines]
                break
    else:
        raise IndentationError(f"In function {func.__name__}")

    src_lines = [line + '\n' for line in src_lines]

    # write file
    if os.environ.get("INSIDE_NETVM", False):

        # add one indentation level (only spaces suported atm)
        # and newline to all lines
        src_lines = [f"    {line}" for line in src_lines]    

        # add exception relay machinery
        src_lines.insert(0, "try:\n")
        src_lines.append(
            "\nexcept Exception as e:\n"
            "    sys.stderr.write(traceback.format_exc())\n"
        )

        random_id = ''.join([
            random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(16)
        ])
        source_path = f"/root/scripts/{func.__name__}-{random_id}.py"

        with open(source_path, "w+") as source_file:
            source_file.writelines([
                f"import sys\n",
                *[f"sys.path.append(\'{path}\')\n" for path in sys.path],
                *src_lines
            ])

    else:
        source_file = NamedTemporaryFile(
            prefix=f"{func.__name__}-",
            suffix=".py",
            mode="w+",
            delete=False
        )
        source_file.writelines(src_lines)
        source_path = source_file.name

    def direct_call(*args, **kwargs):
        direct_call(*args, **kwargs)

    direct_call.path = source_path

    return direct_call


def as_host(vnet, hostname, link, *args, **kwargs):

    def wrapper(func):
        func = as_script(func)
        func.host = vnet.addHost(hostname, *args, **kwargs)
        vnet.addLink(func.host, link)

        def _start_proc():
            func.proc = func.host.popen(
                [sys.executable, func.path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

        def _ip_addr():
            return func.host.cmd('ip addr')

        func.start_host = _start_proc
        func.ipaddr = _ip_addr

        return func

    return wrapper


@pytest.fixture
def vnet():
    vnet = Mininet(controller=Controller)
    vnet.addController('c0')
    yield vnet
    vnet.stop()