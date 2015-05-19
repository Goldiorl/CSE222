from mininet.net import Mininet
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.node import UserSwitch
from mininet.node import RemoteController
from mininet.log import setLogLevel
from mininet.link import TCLink

setLogLevel('info')

class SliceableSwitch(UserSwitch):
    def __init__(self, name, **kwargs):
        UserSwitch.__init__(self, name,'' , **kwargs)
        
class MyTopo(Topo):
    def __init__( self ):
        "Create custom topo."
        # Initialize topology
        Topo.__init__( self )
        # Add hosts and switches
        host01 = self.addHost('h1')
        host02 = self.addHost('h2')
        switch01 = self.addSwitch('s1')
        # Add links
        http_link_config = {'bw': 10,'delay':10000}
        self.addLink(host01, switch01)
        self.addLink(host02, switch01, **http_link_config)

def genericTest(topo):
    net = Mininet(topo=topo, switch=SliceableSwitch,controller=RemoteController,link=TCLink)
    net.start()
    CLI(net)
    net.stop()

def main():
    topo = MyTopo()
    genericTest(topo)

if __name__ == '__main__':
    main()
