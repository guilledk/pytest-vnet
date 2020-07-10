# `pytest-vnet`

`pytest-vnet` is a `pytest` plugin for running software defined network tests inside a docker container with `mininet`, the plugin will manage the python envoirment inside the container to match the hosts python version or a custom one, load tests into the container, run them and return results.

## Install this package:

	pip install git+git://github.com/guilledk/pytest-vnet.git

## Build base netvm image (will be automatic in the future):

	docker build --tag pytest-vnet:netvm netvm/

## Run your test:

	pytest-vnet test_net.py