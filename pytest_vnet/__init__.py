#!/usr/bin/env python3

import os
import re
import sys
import docker
import pathlib

from docker.types import Mount

from typing import Optional

from pathlib import Path

from tempfile import TemporaryFile, TemporaryDirectory

from ._utils import NonZeroExitcode, stream_run, background_run


PYTHON_VERSION = f"{sys.version_info[0]}."\
    f"{sys.version_info[1]}."\
    f"{sys.version_info[2]}"


def prepare_container(target_version: Optional[str] = None):

    if target_version is None:
        target_version = PYTHON_VERSION

    client = docker.from_env()

    print("instantiating container", end="...", flush=True)
    cont = client.containers.create(
        "pytest-vnet:netvm",
        tty=True
    )

    cont.start()
    print("done!")

    print(f"installing python {target_version}:")
    try:
        """Get a copy of the source of the currently running python version
        and untar it.
        """
        background_run(
            cont,
            ["curl", "-O", f"https://www.python.org/ftp/python/{target_version}/Python-{target_version}.tar.xz"],
            workdir="/root"
        )
        background_run(
            cont,
            ["tar", "-xf", f"Python-{target_version}.tar.xz"],
            workdir="/root"
        )

        # Configure, Compile & Install
        background_run(
            cont,
            ["./configure"],
            workdir=f"/root/Python-{target_version}"
        )
        background_run(
            cont,
            ["make", "-j", "2"],
            workdir=f"/root/Python-{target_version}"
        )
        background_run(
            cont,
            ["make", "install"],
            workdir=f"/root/Python-{target_version}"
        )

    except NonZeroExitcode as ex:
        cont.stop()
        cont.remove()
        print(ex)

    else:
        # Save the image
        cont.commit(f"pytest-vnet:netvm-{target_version}")

    if cont.status == "running":
        cont.stop()

    client.close()

    print(f"container pytest-vnet:netvm-{target_version} ready.")


def run_in_netvm(run_target: Path):

    client = docker.from_env()

    # Read current sys.path, and create bind mounts to container /root/lib
    dynmounts = []
    sys_path_targets = []

    for source_path in sys.path:

        # Replace all whats in front of "lib/python" in paths with /root
        search = re.search("lib/python", source_path)
        if search:
            start_idx = search.start()
            target_path = f"/root/{source_path[start_idx:]}"

            # If path exists create, read only bind mount
            if pathlib.Path(source_path).exists():
                sys_path_targets.append(target_path)
                dynmounts.append(
                    Mount(
                        target_path,
                        source_path,
                        "bind",
                        read_only=True
                    )
                )

    with TemporaryDirectory() as tmpdirname:
        with open(f"{tmpdirname}/{run_target.name}", "w") as tmp_run:
            with open(run_target, "r") as src:
                # Patch up target file, insert sys.path appends on top
                tmp_run.write("import sys\n")
                for path in sys_path_targets:
                    tmp_run.write(f"sys.path.append(\"{path}\")\n")

                # Write rest of the file
                tmp_run.write(src.read())

        # Instance container
        cont = client.containers.create(
            f"pytest-vnet:netvm-{PYTHON_VERSION}",
            privileged=True,
            tty=True,
            mounts=dynmounts +
                [
                    Mount(
                        "/root/test",
                        tmpdirname,
                        "bind"
                    )
                ]
            )

        cont.start()

        # Restart openvswitch just in case
        cont.exec_run("service openvswitch-switch start")

        # Run target
        stream_run(
            cont,
            ["python3", run_target.name],
            workdir="/root/test"
        )

        cont.stop()
        cont.remove()