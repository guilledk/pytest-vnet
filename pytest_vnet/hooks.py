#!/usr/bin/env python3

import docker
import inspect
import pytest_vnet

from typing import Optional

from tempfile import TemporaryFile, TemporaryDirectory

from pytest import Item
from _pytest.runner import CallInfo
from _pytest.python import Function

from pytest_vnet import DOCKERC

from docker.models.containers import Container


TEST_VM: Optional[Container] = None


def pytest_addoption(parser):
    parser.addini(
        "netvm_required",
        "enable pytest-vnet",
        type="bool",
        default=False,
    )


def pytest_configure(config):
    # So that it shows up in 'pytest --markers' output:
    config.addinivalue_line(
        "markers", "run_in_netvm: "
        "mark the test as a self contained mininet test; "
        "it will be run inside a netvm container"
    )


def pytest_sessionstart(session):

	if not session.config.getini("netvm_required"):
		return

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
	if item.get_closest_marker("run_in_netvm") is not None and \
		isinstance(item, Function):

		ihook = item.ihook
		ihook.pytest_runtest_logstart(nodeid=item.nodeid, location=item.location)

		# with TemporaryDirectory() as tmpdirname:
		#     with open(f"{tmpdirname}/{item.name}.py", "w") as tmp_run:
		#         with open(run_target, "r") as src:
		#             # Patch up target file, insert sys.path appends on top
		#             tmp_run.write("import sys\n")
		#             for path in sys_path_targets:
		#                 tmp_run.write(f"sys.path.append(\"{path}\")\n")

		#             # Write rest of the file
		#             tmp_run.write(src.read())

		with open("test.py", "w") as tmp_test:

			func_source = inspect.getsource(item.function)

			first_newline = func_source.find('\n', 0)

			tmp_test.write(func_source[first_newline+1:])

		call = CallInfo(None, 0, 0, 0, "call")
		report = ihook.pytest_runtest_makereport(item=item, call=call)
		ihook.pytest_runtest_logreport(report=report)
		ihook.pytest_runtest_logfinish(nodeid=item.nodeid, location=item.location)
		return True