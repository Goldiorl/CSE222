#!/usr/bin/python

from mininet.topo import Topo

class FVTopo(Topo):

    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Create template host, switch, and link
        hconfig = {'inNamespace':True}
        http_link_config = {'bw': 5}
        #video_link_config = {'bw': 10}
        host_link_config = {}

        # Create switch nodes
        for i in range(2):
            sconfig = {'dpid': "%016x" % (i+1)}
            self.addSwitch('s%d' % (i+1), **sconfig)

        # Create host nodes
        for i in range(3):
            self.addHost('h%d' % (i+1), **hconfig)

        # Add switch links
	self.addLink('s1', 's2', **http_link_config)
        self.addLink('h1', 's1', **host_link_config)
        self.addLink('h2', 's1', **host_link_config)
        #self.addLink('h3', 's1', **host_link_config)
        #self.addLink('h4', 's1', **host_link_config)
        #self.addLink('h5', 's1', **host_link_config)
        self.addLink('h3', 's2', **host_link_config)

topos = { 'fvtopo': ( lambda: FVTopo() ) }
