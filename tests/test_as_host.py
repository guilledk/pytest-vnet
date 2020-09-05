#!/usr/bin/env python3
import pytest

from pytest_vnet import vnet, as_host, HostException


def test_raise(vnet):
    switch = vnet.addSwitch("s3")

    @as_host(vnet, 'h1', switch, ip='10.0.0.1')
    def raiser():
        assert False

    vnet.start()
    raiser.start_host()

    with pytest.raises(HostException) as excinfo:
        raiser.wait()

    assert "assert False" in str(excinfo.value)
    assert "AssertionError" in str(excinfo.value)


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
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('10.0.0.1', 50090))
            s.sendall("Hello world through a virtual socket!".encode('utf-8'))

    vnet.start()
    receiver.start_host()
    sender.start_host()
    receiver.proc.wait(timeout=3)

    assert b'hello' in receiver.proc.stdout.read()


def test_internet_hello(vnet):
    """
       'internet'
       server (h0)
           |
       switch (s0)
           |
    ----------------
    |              |
   isp 1          isp 2
   (nat1)         (nat2)
    |              |
  switch 1       switch 2
   (s1)           (s2)
    |              |
  client 1       client 2
   (h1)           (h2)

    """

    switch_inet = vnet.addSwitch('s0')
   
    @as_host(vnet, 'h0', switch_inet)
    def server():
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 50090))
            s.listen(1)
            while True:
                conn, addr = s.accept()
                with conn:
                    conn.sendall('hello client!'.encode('utf-8'))

    clients = []
    for i in range(1, 3):
        inet_iface = f"nat_{i}-eth0"
        local_iface = f"nat_{i}-eth1"
        local_addr = f"192.168.{i}.1"
        local_subnet = f"192.168.{i}.0/24"
        nat_params = { 'ip' : f"{local_addr}/24" }

        vnet.ipBase = local_subnet
        # ^ needed to overwrite default subnet passed to addNAT
        nat = vnet.addNAT(
            f"nat{i}",
            inetIntf=inet_iface,
            localIntf=local_iface
        )

        switch = vnet.addSwitch(f"s{i}")
        vnet.addLink(nat, switch_inet, intfName1=inet_iface)
        vnet.addLink(nat, switch, intfName1=local_iface, params1=nat_params)

        @as_host(
            vnet, f"h{i}", switch,
            ip=f"192.168.{i}.100/24",
            defaultRoute=f"via {local_addr}"
        )
        def client():
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('10.0.0.1', 50090))
                data = s.recv(1024)
                assert data == b'hello client!'

        clients.append(client)

    vnet.start()
    server.start_host()
    for client in clients:
        client.start_host()

    for client in clients:
        client.wait(timeout=3)

    server.proc.kill()
    server.wait()