#!/usr/bin/env python3

import pytest
import inspect

from typing import Optional

from tempfile import TemporaryDirectory

from pytest import Item
from _pytest.runner import CallInfo
from _pytest.python import Function

from pytest_vnet.plugin import VirtualNetworkPlugin

VNET_PLUGIN: Optional[VirtualNetworkPlugin] = None

def pytest_collection_modifyitems(session, config, items):
    global VNET_PLUGIN

    VNET_PLUGIN = VirtualNetworkPlugin(items)

    if VNET_PLUGIN.vm_required:
        VNET_PLUGIN.init_container()


def pytest_sessionfinish(session, exitstatus):
    global VNET_PLUGIN

    if VNET_PLUGIN:
        VNET_PLUGIN.shutdown()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):

    def func_wrapper():
        ...

    if item.get_closest_marker("run_in_netvm") is not None and \
        isinstance(item, Function):

        item.obj = func_wrapper

    yield