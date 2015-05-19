#!/usr/bin/python

import re
import sys

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.topolib import TreeTopo
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.link import TCLink, Intf
from mininet.util import quietRun

setLogLevel( 'info' )


class FVTopo(Topo):


    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Create template host, switch, and link
        hconfig = {'inNamespace':True}
        http_link_config = {'bw': 10}
        #video_link_config = {'bw': 10}
        host_link_config = {}

        # Create switch nodes
        for i in range(2):
            sconfig = {'dpid': "%016x" % (i+1)}
            self.addSwitch('s%d' % (i+1), **sconfig)

        # Create host nodes
        for i in range(6):
            self.addHost('h%d' % (i+1), **hconfig)

        # Add switch link
	self.addLink('h1', 's1', **host_link_config)
        self.addLink('h2', 's1', **host_link_config)
        self.addLink('h3', 's1', **host_link_config)
	self.addLink('h4', 's2', **host_link_config)
        self.addLink('h5', 's2', **host_link_config)
        self.addLink('h6', 's2', **host_link_config)
        self.addLink('s1', 's2', **http_link_config)

topos = { 'fvtopo': ( lambda: FVTopo() ) }


c0 = RemoteController('c0',ip='127.0.0.1', port=6633)
c1 = Controller('c1', port=6634)

cmap = { 's1': c0, 's2': c1 }

class MultiSwitch( OVSSwitch ):
    "Custom Switch() subclass that connects to different controllers"
    def start( self, controllers ):
        return OVSSwitch.start( self, [ cmap[ self.name ] ] )


net = Mininet(topo=FVTopo(), switch=MultiSwitch, link=TCLink , build=False)
net.addController(c1)
net.build()
s1 = net.getNodeByName('s1')
net.start()
s1.cmdPrint('sh swsetup.sh')
c1 = net.getNodeByName('c1')
c1.cmdPrint('sh ovsdb.sh')
h4 = net.getNodeByName('h4')
h4.cmdPrint('python -m SimpleHTTPServer 80 &')
'''
CLI( net )
h1 = net.getNodeByName('h1')
h2 = net.getNodeByName('h2')
h3 = net.getNodeByName('h3')
h4 = net.getNodeByName('h4')
h5 = net.getNodeByName('h5')
h6 = net.getNodeByName('h6')
h1.cmdPrint(" iperf -s -i 0.5 -t 60 >  h1.txt &")
h2.cmdPrint(" iperf -s -i 0.5 -t 60 >  h2.txt &")
h3.cmdPrint(" iperf -s -i 0.5 -t 60 >  h3.txt &")
h4.cmdPrint(" iperf -c 10.0.0.1 -i 0.5 -t 60 >h4.txt  & ")
h5.cmdPrint(" iperf -c 10.0.0.2 -i 0.5 -t 60 >h5.txt  & ")
h6.cmdPrint(" iperf -c 10.0.0.3 -i 0.5 -t 60 >h6.txt  ")
'''
CLI( net)
net.stop()
