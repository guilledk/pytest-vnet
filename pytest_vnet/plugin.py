#!/usr/bin/env python3
import os
import sys
import random
import inspect
import subprocess

from tempfile import NamedTemporaryFile

import pytest

from mininet.net import Mininet
from mininet.node import Controller


multihost_test = pytest.mark.multihost


def as_script(func):
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