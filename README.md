# `pytest-vnet`

`pytest-vnet` is a `pytest` plugin for running software defined network tests inside a docker container with `mininet`, the plugin will manage the python envoirment inside the container to match the hosts python version or a custom one, load tests into the container, run them and return results.

## Install this package:

	pip install git+git://github.com/guilledk/pytest-vnet.git

## Mark your mininet tests with:

```python
from pytest_vnet import run_in_netvm

@run_in_netvm
def test_net():
	from mininet.net import Mininet
	...
```

## Run your test:

	pytest