# `pytest-vnet`

`pytest-vnet` is a `pytest` plugin for running software defined network tests inside a docker container with `mininet`, the plugin will manage the python envoirment inside the container to match the hosts python version or a custom one, load tests into the container, run them and return results.

## Install this package:

	pip install git+git://github.com/guilledk/pytest-vnet.git

## Mark your mininet tests with:

- `@run_in_netvm`: Will run the test inside the container.
- `@as_script`: Will make the function available as a script inside the container (should only be used inside a `@run_in_netvm` decorated function).

```python
from pytest_vnet import run_in_netvm

@run_in_netvm
def test_vsocket_hello():

    s3 = vnet.addSwitch("s3")

    @as_host(vnet, 'h1', '10.0.0.1', s3)
    def receiver():
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 50007))
            s.listen(1)
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024)
                assert data == b"Hello world through a virtual socket!"

    @as_host(vnet, 'h2', '10.0.0.2', s3)
    def sender():
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('10.0.0.1', 50007))
            s.sendall("Hello world through a virtual socket!".encode('utf-8'))

    vnet.start()
    receiver.start_host()
    sender.start_host()
    receiver.proc.wait(timeout=3)
```

## Run your test:

	pytest