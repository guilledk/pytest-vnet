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

    import time
    from mininet.net import Mininet
    from mininet.node import Controller
    from mininet.util import pmonitor

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