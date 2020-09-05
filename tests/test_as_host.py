#!/usr/bin/env python3
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
                print('hello client!')

    @as_host(vnet, 'h2', s3, ip='10.0.0.2')
    def sender():
        import sys
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('10.0.0.1', 50090))
            s.sendall("Hello world through a virtual socket!".encode('utf-8'))

    vnet.start()
    receiver.start_host()
    sender.start_host()
    receiver.proc.wait(timeout=3)

    assert b'hello' in receiver.proc.stdout.read()