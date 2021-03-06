#!/usr/bin/env python3
from pytest_vnet import vnet


def test_emptynet(vnet):
    s3 = vnet.addSwitch("s3")

    h1 = vnet.addHost("h1", ip="10.0.0.1")
    h2 = vnet.addHost("h2", ip="10.0.0.2")

    vnet.addLink(h1, s3)
    vnet.addLink(h2, s3)

    vnet.start()

    assert "10.0.0.1" in h1.cmd("ip addr")
    assert "10.0.0.2" in h2.cmd("ip addr")