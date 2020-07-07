#!/usr/bin/env python3

import sys
import docker

from docker.types import Mount

from _utils import stream_run


# Get envoirment python version
python_version = f"{sys.version_info[0]}."\
	f"{sys.version_info[1]}."\
	f"{sys.version_info[2]}"

client = docker.from_env()

cont = client.containers.create(
	"pytest-vnet:netvm",
	tty=True
)

cont.start()

"""Get a copy of the source of the currently running python version
and untar it.
"""
stream_run(
	cont,
	["curl", "-O", f"https://www.python.org/ftp/python/{python_version}/Python-{python_version}.tar.xz"],
	workdir="/root"
)
stream_run(
	cont,
	["tar", "-xf", f"Python-{python_version}.tar.xz"],
	workdir="/root"
)

# Configure, Compile & Install
stream_run(
	cont,
	["./configure"],
	workdir=f"/root/Python-{python_version}"
)
stream_run(
	cont,
	["make", "-j", "2"],
	workdir=f"/root/Python-{python_version}"
)
stream_run(
	cont,
	["make", "install"],
	workdir=f"/root/Python-{python_version}"
)

# Save the image
cont.commit(f"netvm-{python_version}")

cont.stop()