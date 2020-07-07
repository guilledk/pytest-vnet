#!/usr/bin/env python3

import os
import re
import sys
import docker
import pathlib

from docker.types import Mount

from _utils import stream_run


# Get envoirment python version
python_version = f"{sys.version_info[0]}."\
	f"{sys.version_info[1]}."\
	f"{sys.version_info[2]}"

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

# Instance container
cont = client.containers.create(
	f"netvm-{python_version}",
	privileged=True,
	tty=True,
	mounts=dynmounts +
		[
			Mount(
				"/root/test",
				str(pathlib.Path().absolute()),
				"bind"
			)
		]
	)

cont.start()

run_target = sys.argv[1]

# Patch up target file, insert sys.path appends on top
with open(run_target, "r") as src:
    with open('tmp.py','w') as tmp_run:
        tmp_run.write("import sys\n")
        for path in sys_path_targets:
        	tmp_run.write(f"sys.path.append(\"{path}\")\n")
        tmp_run.write(src.read())

# Restart openvswitch just in case
cont.exec_run("service openvswitch-switch start")

# Run target
stream_run(
	cont,
	["python3", "tmp.py"],
	workdir="/root/test"
)

cont.stop()
cont.remove()

os.remove("tmp.py")