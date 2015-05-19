from mininet.net import Mininet
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.node import UserSwitch
from mininet.node import RemoteController,Controller
from mininet.link import TCLink
from mininet.log import setLogLevel



setLogLevel( 'info' )

class MyTopo(Topo):
    def __init__( self ):
        "Create custom topo."
        # Initialize topology
        Topo.__init__( self )

        hconfig = {'inNamespace':True}
        http_link_config = {'bw': 10}
        host_link_config = {}

        # Add hosts and switches
        host01 = self.addHost('h1',**hconfig)
        host02 = self.addHost('h2',**hconfig)
        host03 = self.addHost('h3',**hconfig)
        host04 = self.addHost('h4',**hconfig)
        host05 = self.addHost('h5',**hconfig)
        host06 = self.addHost('h6',**hconfig)

        #sconfig1 = {'dpid': "%016x" % (1)}
        #sconfig2 = {'dpid': "%016x" % (2)}
        switch01 = self.addSwitch('s1')
        switch02 = self.addSwitch('s2')

        # Add links
        self.addLink('h1', 's1', **host_link_config)
        self.addLink('h2', 's1', **host_link_config)
        self.addLink('h3', 's1', **host_link_config)
        self.addLink('h4', 's2', **host_link_config)
        self.addLink('h5', 's2', **host_link_config)
        self.addLink('h6', 's2', **host_link_config)
        self.addLink('s1', 's2', **host_link_config)

c0 = RemoteController('c0',ip='127.0.0.1', port=6633)
c1 = Controller('c1', port=6634)
cmap = { 's1': c0, 's2': c1 }

class SliceableSwitch(UserSwitch):
    def start( self, controllers ):
        return UserSwitch.start( self,  [ cmap[ self.name ] ])

net = Mininet(topo=MyTopo(), switch=SliceableSwitch, link=TCLink , build=False)
net.addController(c1)
net.build()
net.start()
CLI(net)
net.stop()