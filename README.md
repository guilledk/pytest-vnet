The idea is being able to run  `pytest-vnet mytest.py` and have this wrapper load the test to a docker container with mininet, run pytest on it and return its output.

build image:

	`docker build --tag pytest-vnet:netvm netvm/`

run interactive shell:

	`docker run --it --privileged pytest-vnet:netvm`