#!/usr/bin/env python3

import docker
import pytest_vnet

from typing import Optional

from pytest import Item
from _pytest.runner import CallInfo

from pytest_vnet import DOCKERC

from docker.models.containers import Container


TEST_VM: Optional[Container] = None

def pytest_sessionstart(session):

	global TEST_VM

	# Check if base image is present or pull it
	try:
		netvm_base_image = DOCKERC.images.get("guilledk/pytest-vnet:netvm")

	except docker.errors.ImageNotFound:
		print("base netvm image not found, pulling 238.3mb", end=" ... ", flush=True)
		DOCKERC.images.pull("guilledk/pytest-vnet", "netvm")
		print("done")

	print("starting netvm", end=" ... ", flush=True)
	# Check if python enabled version is present or create it
	try:
		TEST_VM = pytest_vnet.initiate_container()

	except docker.errors.ImageNotFound:
		print(
			f"installing python {pytest_vnet.PYTHON_VERSION}",
			end=" ... ", flush=True
		)
		pytest_vnet.install_python_container()
		TEST_VM = pytest_vnet.initiate_container()

	finally:
		print(f"done")

def pytest_sessionfinish(session, exitstatus):
	global TEST_VM
	if TEST_VM is not None:
		print("\nstopping netvm", end=" ... ", flush=True)
		TEST_VM.stop()
		TEST_VM.remove()
		print("done")


def pytest_runtest_protocol(item: Item, nextitem: Optional[Item]) -> bool:
	if "RUN_IN_NETVM" in [mark.name for mark in item.iter_markers()]:
		ihook = item.ihook
		ihook.pytest_runtest_logstart(nodeid=item.nodeid, location=item.location)
		call = CallInfo(None, 0, 0, 0, "call")
		report = ihook.pytest_runtest_makereport(item=item, call=call)
		ihook.pytest_runtest_logreport(report=report)
		ihook.pytest_runtest_logfinish(nodeid=item.nodeid, location=item.location)
		return True