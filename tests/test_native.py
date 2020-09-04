import sys
import subprocess

from pytest_vnet import vnet, as_host, as_script

def test_emptynet(vnet):
    s3 = vnet.addSwitch("s3")

    h1 = vnet.addHost("h1", ip="10.0.0.1")
    h2 = vnet.addHost("h2", ip="10.0.0.2")

    vnet.addLink(h1, s3)
    vnet.addLink(h2, s3)

    vnet.start()

    assert "10.0.0.1" in h1.cmd("ip addr")
    assert "10.0.0.2" in h2.cmd("ip addr")


def test_echo_script():

    @as_script
    def echo():
        import sys
        print(sys.argv[1])

    message = "Hello World!"

    assert subprocess.check_output(
        [sys.executable, echo.path, message]
    ).decode('utf-8').rstrip() == message


def test_inner_import():

    @as_script
    def inner():
        import pytest_vnet
        print("OK")

    assert subprocess.check_output(
        [sys.executable, inner.path]
    ).decode('utf-8').rstrip() == "OK"


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