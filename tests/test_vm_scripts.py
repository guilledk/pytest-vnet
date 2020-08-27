from pytest_vnet import run_in_netvm

@run_in_netvm
def test_echo_script():
    import subprocess

    message = "Hello World!"

    out = subprocess.check_output(
        ['python3', vm_scripts["echo"], message]
    ).decode('utf-8').rstrip()

    assert out == message


@run_in_netvm
def test_echo_server_client():
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

    server_proc = h1.popen(["python3", vm_scripts['echo_server']])
    client_proc = h2.popen(["python3", vm_scripts['echo_client'], message])

    assert server_proc.stdout.read() == client_proc.stdout.read()

    net.stop()