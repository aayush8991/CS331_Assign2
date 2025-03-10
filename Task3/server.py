import socket
import time
import argparse
import os
import threading
from collections import deque
from datetime import datetime

class PerformanceMonitor:
    def __init__(self):
        self.bytes_received = 0
        self.useful_bytes_received = 0
        self.packets_received = 0
        self.packets_lost = 0
        self.packet_sizes = []
        self.start_time = None
        self.end_time = None
        
    def start(self):
        self.start_time = time.time()
        
    def stop(self):
        self.end_time = time.time()
        
    def add_packet(self, data_len, is_useful=True):
        self.bytes_received += data_len
        self.packets_received += 1
        self.packet_sizes.append(data_len)
        if is_useful:
            self.useful_bytes_received += data_len
            
    def register_lost_packet(self):
        self.packets_lost += 1
            
    def get_metrics(self):
        duration = self.end_time - self.start_time
        throughput = self.bytes_received / duration if duration > 0 else 0
        goodput = self.useful_bytes_received / duration if duration > 0 else 0
        loss_rate = self.packets_lost / (self.packets_received + self.packets_lost) if self.packets_received + self.packets_lost > 0 else 0
        max_packet_size = max(self.packet_sizes) if self.packet_sizes else 0
        
        return {
            "duration": duration,
            "throughput": throughput,
            "goodput": goodput,
            "packet_loss_rate": loss_rate,
            "max_packet_size": max_packet_size,
            "total_packets": self.packets_received,
            "total_bytes": self.bytes_received,
            "useful_bytes": self.useful_bytes_received
        }


def run_server(port, use_nagle, use_delayed_ack, test_duration=120):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Set TCP_NODELAY option to disable Nagle's algorithm (True = disabled)
    server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 0 if use_nagle else 1)
    
    # The TCP_QUICKACK option is Linux-specific
    # For other platforms, this might need adjustment
    try:
        # Set TCP_QUICKACK option to disable delayed ACK (True = disabled delaying ACKs)
        server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 0 if use_delayed_ack else 1)
        delayed_ack_support = True
    except AttributeError:
        print("Warning: TCP_QUICKACK not supported on this platform.")
        delayed_ack_support = False
    
    server_socket.bind(('localhost', port))
    server_socket.listen(1)
    
    print(f"Server started on port {port}")
    print(f"Configuration: Nagle's Algorithm: {'Enabled' if use_nagle else 'Disabled'}, "
          f"Delayed-ACK: {'Enabled' if use_delayed_ack else 'Disabled'}")
    
    conn, addr = server_socket.accept()
    print(f"Connection from {addr}")
    
    # Set options for the connection socket as well
    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 0 if use_nagle else 1)
    if delayed_ack_support:
        try:
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 0 if use_delayed_ack else 1)
        except:
            print("Warning: Could not set TCP_QUICKACK on the connection socket.")
    
    # Prepare for receiving data
    monitor = PerformanceMonitor()
    monitor.start()
    
    total_data = bytearray()
    
    # Set a timeout for the test duration
    conn.settimeout(test_duration + 5)  # Give a little extra time for completion
    
    try:
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                
                monitor.add_packet(len(data))
                total_data.extend(data)
                
                # For testing - print current progress
                print(f"\rReceived: {len(total_data)} bytes in {monitor.packets_received} packets", end="")
                
            except socket.timeout:
                print("\nConnection timed out after waiting for data")
                break
    except Exception as e:
        print(f"\nError during data reception: {e}")
    finally:
        print("\nTransmission complete")
        monitor.stop()
        conn.close()
        server_socket.close()
    
    # Calculate and display metrics
    metrics = monitor.get_metrics()
    
    print("\n----- Performance Metrics -----")
    print(f"Configuration: Nagle's Algorithm: {'Enabled' if use_nagle else 'Disabled'}, "
          f"Delayed-ACK: {'Enabled' if use_delayed_ack else 'Disabled'}")
    print(f"Test Duration: {metrics['duration']:.2f} seconds")
    print(f"Total Data Received: {metrics['total_bytes']} bytes")
    print(f"Total Packets: {metrics['total_packets']}")
    print(f"Throughput: {metrics['throughput']:.2f} bytes/sec")
    print(f"Goodput: {metrics['goodput']:.2f} bytes/sec")
    print(f"Packet Loss Rate: {metrics['packet_loss_rate']:.4f}")
    print(f"Maximum Packet Size: {metrics['max_packet_size']} bytes")
    
    # Save results to a file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"server_results_nagle{'On' if use_nagle else 'Off'}_delayedack{'On' if use_delayed_ack else 'Off'}_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("----- Performance Metrics -----\n")
        f.write(f"Configuration: Nagle's Algorithm: {'Enabled' if use_nagle else 'Disabled'}, "
                f"Delayed-ACK: {'Enabled' if use_delayed_ack else 'Disabled'}\n")
        f.write(f"Test Duration: {metrics['duration']:.2f} seconds\n")
        f.write(f"Total Data Received: {metrics['total_bytes']} bytes\n")
        f.write(f"Total Packets: {metrics['total_packets']}\n") 
        f.write(f"Throughput: {metrics['throughput']:.2f} bytes/sec\n")
        f.write(f"Goodput: {metrics['goodput']:.2f} bytes/sec\n")
        f.write(f"Packet Loss Rate: {metrics['packet_loss_rate']:.4f}\n")
        f.write(f"Maximum Packet Size: {metrics['max_packet_size']} bytes\n")
    
    print(f"Results saved to {filename}")
    
    return metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TCP Server for performance testing')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    parser.add_argument('--nagle', action='store_true', help='Enable Nagle\'s algorithm')
    parser.add_argument('--delayed-ack', action='store_true', help='Enable Delayed-ACK')
    parser.add_argument('--duration', type=int, default=120, help='Test duration in seconds')
    
    args = parser.parse_args()
    
    run_server(args.port, args.nagle, args.delayed_ack, args.duration)