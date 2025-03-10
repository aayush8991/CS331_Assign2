import socket
import time
import argparse
import os
import random
import threading
from datetime import datetime

class RateLimiter:
    def __init__(self, rate_bytes_per_sec):
        self.rate = rate_bytes_per_sec
        self.last_check = time.time()
        self.bytes_sent = 0
        
    def limit(self, bytes_to_send):
        current_time = time.time()
        time_passed = current_time - self.last_check
        
        # Calculate how many bytes we're allowed to send based on time passed
        allowed_bytes = self.rate * time_passed
        
        if self.bytes_sent + bytes_to_send > allowed_bytes:
            # We need to wait
            bytes_over_limit = (self.bytes_sent + bytes_to_send) - allowed_bytes
            time_to_wait = bytes_over_limit / self.rate
            time.sleep(time_to_wait)
            
            # Reset counters
            self.last_check = time.time()
            self.bytes_sent = 0
        else:
            # Update byte count
            self.bytes_sent += bytes_to_send

def run_client(server_host, server_port, use_nagle, use_delayed_ack, data_size=4096, rate=40, duration=120):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Set TCP_NODELAY option to disable Nagle's algorithm (True = disabled)
    client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 0 if use_nagle else 1)
    
    # The TCP_QUICKACK option is Linux-specific
    # For other platforms, this might need adjustment
    try:
        # Set TCP_QUICKACK option to disable delayed ACK (True = disabled delaying ACKs)
        client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 0 if use_delayed_ack else 1)
        delayed_ack_support = True
    except AttributeError:
        print("Warning: TCP_QUICKACK not supported on this platform.")
        delayed_ack_support = False
    
    try:
        client_socket.connect((server_host, server_port))
        print(f"Connected to server {server_host}:{server_port}")
        print(f"Configuration: Nagle's Algorithm: {'Enabled' if use_nagle else 'Disabled'}, "
              f"Delayed-ACK: {'Enabled' if use_delayed_ack else 'Disabled'}")
        
        # Generate test data (random data of specified size)
        test_data = os.urandom(data_size)
        
        # Initialize rate limiter
        rate_limiter = RateLimiter(rate)
        
        bytes_sent = 0
        packets_sent = 0
        chunk_sizes = []
        
        # Get start time
        start_time = time.time()
        end_time = start_time + duration
        
        # Send data at specified rate
        while time.time() < end_time:
            # Decide on a chunk size (between 1 and min(40, remaining))
            remaining = data_size - (bytes_sent % data_size)
            max_chunk = min(rate, remaining)
            chunk_size = random.randint(1, max_chunk)
            
            # Get the next chunk of data (cycling through the test data)
            position = bytes_sent % data_size
            chunk = test_data[position:position + chunk_size]
            
            # Apply rate limiting
            rate_limiter.limit(len(chunk))
            
            # Send the chunk
            client_socket.send(chunk)
            
            # Update statistics
            bytes_sent += len(chunk)
            packets_sent += 1
            chunk_sizes.append(len(chunk))
            
            # Display progress
            elapsed = time.time() - start_time
            print(f"\rSent: {bytes_sent} bytes in {packets_sent} packets, "
                  f"Elapsed: {elapsed:.1f}/{duration} seconds, "
                  f"Rate: {bytes_sent/elapsed:.2f} bytes/sec", end="")
            
            # Small pause to give CPU time to other processes
            time.sleep(0.01)
        
        # Final statistics
        actual_duration = time.time() - start_time
        print("\n----- Client Statistics -----")
        print(f"Configuration: Nagle's Algorithm: {'Enabled' if use_nagle else 'Disabled'}, "
              f"Delayed-ACK: {'Enabled' if use_delayed_ack else 'Disabled'}")
        print(f"Test Duration: {actual_duration:.2f} seconds")
        print(f"Bytes Sent: {bytes_sent}")
        print(f"Packets Sent: {packets_sent}")
        print(f"Average Rate: {bytes_sent/actual_duration:.2f} bytes/sec")
        print(f"Average Packet Size: {sum(chunk_sizes)/len(chunk_sizes):.2f} bytes")
        print(f"Maximum Packet Size: {max(chunk_sizes)} bytes")
        
        # Save results to a file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"client_results_nagle{'On' if use_nagle else 'Off'}_delayedack{'On' if use_delayed_ack else 'Off'}_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write("----- Client Statistics -----\n")
            f.write(f"Configuration: Nagle's Algorithm: {'Enabled' if use_nagle else 'Disabled'}, "
                  f"Delayed-ACK: {'Enabled' if use_delayed_ack else 'Disabled'}\n")
            f.write(f"Test Duration: {actual_duration:.2f} seconds\n")
            f.write(f"Bytes Sent: {bytes_sent}\n")
            f.write(f"Packets Sent: {packets_sent}\n")
            f.write(f"Average Rate: {bytes_sent/actual_duration:.2f} bytes/sec\n")
            f.write(f"Average Packet Size: {sum(chunk_sizes)/len(chunk_sizes):.2f} bytes\n")
            f.write(f"Maximum Packet Size: {max(chunk_sizes)} bytes\n")
        
        print(f"Results saved to {filename}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TCP Client for performance testing')
    parser.add_argument('--host', type=str, default='localhost', help='Server hostname or IP')
    parser.add_argument('--port', type=int, default=8080, help='Server port')
    parser.add_argument('--nagle', action='store_true', help='Enable Nagle\'s algorithm')
    parser.add_argument('--delayed-ack', action='store_true', help='Enable Delayed-ACK')
    parser.add_argument('--data-size', type=int, default=4096, help='Size of test data in bytes')
    parser.add_argument('--rate', type=int, default=40, help='Data rate in bytes per second')
    parser.add_argument('--duration', type=int, default=120, help='Test duration in seconds')
    
    args = parser.parse_args()
    
    run_client(args.host, args.port, args.nagle, args.delayed_ack, args.data_size, args.rate, args.duration)