from pytest_vnet import run_in_netvm

@run_in_netvm
def test_echo_script():

    @as_script
    def echo():
        import sys
        print(sys.argv[1])

    import subprocess

    message = "Hello World!"

    assert subprocess.check_output(
        ['python3', echo.path, message]
    ).decode('utf-8').rstrip() == message


@run_in_netvm
def test_inner_import():

    import subprocess

    @as_script
    def inner():
        import pytest_vnet
        print("OK")

    assert subprocess.check_output(
        ['python3', inner.path]
    ).decode('utf-8').rstrip() == "OK"

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