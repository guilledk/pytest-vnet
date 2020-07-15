#!/usr/bin/env python3

import pytest

from typing import Optional

from pytest_vnet.plugin import VirtualNetworkPlugin


VNET_PLUGIN: Optional[VirtualNetworkPlugin] = None


def pytest_collection_modifyitems(session, config, items):
    global VNET_PLUGIN

    VNET_PLUGIN = VirtualNetworkPlugin(items)

    if VNET_PLUGIN.vm_required:
        VNET_PLUGIN.init_container()


def pytest_sessionfinish(session, exitstatus):
    global VNET_PLUGIN

    if VNET_PLUGIN.vm_required:
        VNET_PLUGIN.shutdown()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    global VNET_PLUGIN

    def func_wrapper():
        ...

    if item in VNET_PLUGIN.vm_items:
        item.obj = func_wrapper

    yield