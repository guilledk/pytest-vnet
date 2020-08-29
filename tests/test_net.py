from pytest_vnet import run_in_netvm

@run_in_netvm
def test_run_in_netvm():
    assert True

@run_in_netvm
def test_emptynet():
    s3 = vnet.addSwitch("s3")

    h1 = vnet.addHost("h1", ip="10.0.0.1")
    h2 = vnet.addHost("h2", ip="10.0.0.2")

    vnet.addLink(h1, s3)
    vnet.addLink(h2, s3)

    vnet.start()

    assert "10.0.0.1" in h1.cmd("ip addr")
    assert "10.0.0.2" in h2.cmd("ip addr")