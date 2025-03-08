from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

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

def run_experiment():
    topo = MyTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    # Set congestion control schemes
    protocols = ['cubic', 'vegas', 'htcp']
    for protocol in protocols:
        print(f"Testing {protocol}...")
        # Configure congestion control on all hosts
        for host in net.hosts:
            host.cmd(f'sysctl -w net.ipv4.tcp_congestion_control={protocol}')

        # Run iperf3 server on H7
        h7 = net.get('h7')
        h7.cmd('iperf3 -s &')

        # Run iperf3 clients on H1-H6
        for i in range(1, 7):
            host = net.get(f'h{i}')
            host.cmd(f'iperf3 -c {h7.IP()} -b 10M -P 10 -t 150 -C {protocol} &')

        # Wait for experiments to complete
        CLI(net)  # Use CLI to interact with the network

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run_experiment()