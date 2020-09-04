# `pytest-vnet`

`pytest-vnet` is a `pytest` plugin for running software defined network tests, by providing pythonic apis to `mininet`.

`mininet` uses linux network namespaces to implement its core functionality, for `windows` and `darwin` envoriments `pytest_vnet` uses a `docker` container were `mininet` is available and dynamicaly a python envoirment is installed to match the hosts python version then tests run and the results are forwarded to the hosts.

- `@as_script`: Will make the function available as a script.
- `@as_host`: Will create a mininet host and will provide ``start_host`` to launch the function code as a process inside that host.
- `@run_in_netvm`: Will run the test inside the container.

## Install this package:

	pip install git+git://github.com/guilledk/pytest-vnet.git

## Example:

```python
from pytest_vnet import vnet, as_host

def test_vsocket_hello(vnet):

    s3 = vnet.addSwitch("s3")

    @as_host(vnet, 'h1', s3, ip='10.0.0.1')
    def receiver():
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 50090))
            s.listen(1)
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024)
                assert data == b"Hello world through a virtual socket!"

    @as_host(vnet, 'h2', s3, ip='10.0.0.2')
    def sender():
        import sys
        import socket
        sys.stderr.write("test")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('10.0.0.1', 50090))
            s.sendall("Hello world through a virtual socket!".encode('utf-8'))

    vnet.start()
    receiver.start_host()
    sender.start_host()
    receiver.proc.wait(timeout=3)
```

## Run your test:

	sudo pytest

## Run tests in container:

    pytest --enable-netv