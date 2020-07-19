from pytest_vnet import run_in_netvm

@run_in_netvm
def test_imports():
    from mininet.net import Mininet

    assert True

@run_in_netvm
def test_emptynet():
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

    assert "10.0.0.1" in h1.cmd("ip addr")
    assert "10.0.0.2" in h2.cmd("ip addr")

    net.stop()