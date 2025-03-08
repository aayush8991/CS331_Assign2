from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink
from mininet.node import OVSSwitch
from mininet.node import RemoteController

class MyTopo(Topo):
    def __init__(self):
        Topo.__init__(self)
        
        # Add hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')
        
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        
        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(s1, s2)
        self.addLink(h3, s2)
        self.addLink(s2, s3)
        self.addLink(h4, s3)
        self.addLink(h5, s3)
        self.addLink(s3, s4)
        self.addLink(h6, s4)
        self.addLink(h7, s4)

def run():
    # Create the topology
    topo = MyTopo()
    
    # Create and start the network with a remote controller
    controller = RemoteController('c0', ip='127.0.0.1', port=6653)
    net = Mininet(
        topo=topo,
        link=TCLink,
        switch=OVSSwitch,
        controller=controller
    )
    
    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()