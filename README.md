The idea is being able to run  `pytest-vnet mytest.py` and have this wrapper load the test to a docker container with mininet, run pytest on it and return its output.

CURRENT PROGRESS:

clone this repo:

	`git clone git://github.com/guilledk/pytest-vnet.git`

build image:

	`docker build --tag pytest-vnet:netvm netvm/`

install required python on container:

	`python install_python.py`

run mininet scripts inside container:

	`python run_in_container.py $TARGET`

example:

	`python run_in_container.py test_net.py`

to run interactive shell:

	`docker run --it --privileged pytest-vnet:netvm`