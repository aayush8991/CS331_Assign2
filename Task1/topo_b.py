from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import RemoteController
import time

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
    # Create topology
    topo = MyTopo()
    net = Mininet(topo=topo, controller=RemoteController)
    net.start()
    
    # Start xterm for iperf server on h7
    h7 = net.get('h7')
    h7.cmd('xterm -title "H7 Server" -e "iperf -s -p 5001; bash" &')
    
    # Give server time to start
    time.sleep(2)
    
    # Get client hosts
    h1 = net.get('h1')
    h3 = net.get('h3')
    h4 = net.get('h4')
    time.sleep(15)
    # H1 starts at T=0s
    print("Starting H1 client at T=0s")
    h1.cmd('xterm -title "H1 Client (Cubic)" -e "iperf -c', h7.IP(), '-p 5001 -b 5M -P 10 -t 150 -i 1 -Z htcp ; bash" &')
    
    # H3 starts at T=15s
    print("Waiting 15s before starting H3...")
    time.sleep(15)
    print("Starting H3 client at T=15s")
    h3.cmd('xterm -title "H3 Client (Cubic)" -e "iperf -c', h7.IP(), '-p 5001 -b 5M -P 10 -t 120 -i 1 -Z htcp ; bash" &')
    
    # H4 starts at T=30s
    print("Waiting 15s before starting H4...")
    time.sleep(15)
    print("Starting H4 client at T=30s")
    h4.cmd('xterm -title "H4 Client (Cubic)" -e "iperf -c', h7.IP(), '-p 5001 -b 5M -P 10 -t 90 -i 1 -Z htcp ; bash" &')
    
    # Open Mininet CLI for further interaction
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()