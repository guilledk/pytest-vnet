
from pytest_vnet import run_in_netvm

@run_in_netvm
def test_ifconfig():

    from mininet.cli import CLI
    from mininet.log import lg, info
    from mininet.net import Mininet
    from mininet.node import OVSKernelSwitch
    from mininet.topolib import TreeTopo

    def ifconfigTest( net ):
        "Run ifconfig on all hosts in net."
        hosts = net.hosts
        for host in hosts:
            info( host.cmd( 'ifconfig' ) )

    lg.setLogLevel( 'info' )
    info( "*** Initializing Mininet and kernel modules\n" )
    OVSKernelSwitch.setup()
    info( "*** Creating network\n" )
    network = Mininet( TreeTopo( depth=2, fanout=2 ), switch=OVSKernelSwitch )
    info( "*** Starting network\n" )
    network.start()
    info( "*** Running ping test\n" )
    network.pingAll()
    info( "*** Running ifconfig test\n" )
    ifconfigTest( network )
    info( "*** Starting CLI (type 'exit' to exit)\n" )
    CLI( network )
    info( "*** Stopping network\n" )
    network.stop()