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
def test_echo_server_client():

    @as_script
    def client_source():
        # Echo client program
        import sys
        import socket

        HOST = '10.0.0.1'  # The remote host
        PORT = 50007  # The same port as used by the server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(sys.argv[1].encode('utf-8'))
            print(s.recv(1024).decode('utf-8'))

    @as_script
    def server_source():
        # Echo server program
        import socket

        HOST = ''  # Symbolic name meaning all available interfaces
        PORT = 50007  # Arbitrary non-privileged port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen(1)
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024)
                if data:
                    print(data.decode('utf-8'))
                    conn.sendall(data)

    from mininet.net import Mininet
    from mininet.node import Controller

    net = Mininet(controller=Controller)

    net.addController("c0")

    h1 = net.addHost("h1", ip="10.0.0.1")
    h2 = net.addHost("h2", ip="10.0.0.2")

    s3 = net.addSwitch("s3")

    net.addLink(h1, s3)
    net.addLink(h2, s3)

    net.start()

    message = "Hello world through a virtual socket!"

    server_proc = h1.popen(["python3", server_source.path])
    client_proc = h2.popen(["python3", client_source.path, message])

    assert server_proc.stdout.read() == client_proc.stdout.read()

    net.stop()
```

## Run your test:

	pytest