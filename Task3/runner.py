import subprocess
import time
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def run_test(nagle, delayed_ack, port, data_size=4096, rate=40, duration=120):
    print(f"\n{'='*80}")
    print(f"Starting Test: Nagle's Algorithm: {'Enabled' if nagle else 'Disabled'}, "
          f"Delayed-ACK: {'Enabled' if delayed_ack else 'Disabled'}")
    print(f"{'='*80}")
    
    # Start server process
    server_cmd = [
        "python3", "server.py",
        "--port", str(port),
    ]
    if nagle:
        server_cmd.append("--nagle")
    if delayed_ack:
        server_cmd.append("--delayed-ack")
    server_cmd.extend(["--duration", str(duration)])
    
    server_process = subprocess.Popen(server_cmd)
    
    # Give server time to start
    time.sleep(2)
    
    # Start client process
    client_cmd = [
        "python3", "client.py",
        "--host", "localhost",
        "--port", str(port),
    ]
    if nagle:
        client_cmd.append("--nagle")
    if delayed_ack:
        client_cmd.append("--delayed-ack")
    client_cmd.extend([
        "--data-size", str(data_size),
        "--rate", str(rate),
        "--duration", str(duration)
    ])
    
    client_process = subprocess.Popen(client_cmd)
    
    # Wait for client to finish
    client_process.wait()
    
    # Give server a moment to finish processing
    time.sleep(2)
    
    # Terminate server if it's still running
    if server_process.poll() is None:
        server_process.terminate()
        server_process.wait()
    
    print(f"\n{'='*80}")
    print("Test completed")
    print(f"{'='*80}\n")
    
    return {
        "nagle": nagle,
        "delayed_ack": delayed_ack
    }

def parse_result_file(filename):
    """Parse a result file and extract metrics"""
    metrics = {}
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Try to convert to float if possible
                try:
                    value = float(value.split()[0])  # Get first part before any units
                except:
                    pass
                
                metrics[key] = value
    
    return metrics

def collect_results(result_dir='.'):
    """Collect and compile all test results"""
    server_results = []
    client_results = []
    
    for filename in os.listdir(result_dir):
        if filename.startswith('server_results_'):
            # Extract configuration from filename
            nagle = 'nagleOn' in filename
            delayed_ack = 'delayedackOn' in filename
            
            metrics = parse_result_file(os.path.join(result_dir, filename))
            metrics['nagle'] = nagle
            metrics['delayed_ack'] = delayed_ack
            server_results.append(metrics)
            
        elif filename.startswith('client_results_'):
            # Extract configuration from filename
            nagle = 'nagleOn' in filename
            delayed_ack = 'delayedackOn' in filename
            
            metrics = parse_result_file(os.path.join(result_dir, filename))
            metrics['nagle'] = nagle
            metrics['delayed_ack'] = delayed_ack
            client_results.append(metrics)
    
    return server_results, client_results

def generate_report(server_results, client_results):
    """Generate a comparison report of all test configurations"""
    if not server_results or not client_results:
        print("No results found to generate report")
        return
    
    # Convert to DataFrames for easier analysis
    server_df = pd.DataFrame(server_results)
    client_df = pd.DataFrame(client_results)
    
    # Create a timestamp for report files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save raw data
    server_df.to_csv(f"server_summary.csv", index=False)
    client_df.to_csv(f"client_summary.csv", index=False)
    
    # Generate comparison report
    report_file = f"comparison_report.txt"
    
    with open(report_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("TCP/IP Performance Comparison with Different Nagle and Delayed-ACK Settings\n")
        f.write("="*80 + "\n\n")
        
        # Server-side metrics
        f.write("-"*80 + "\n")
        f.write("SERVER-SIDE METRICS\n")
        f.write("-"*80 + "\n\n")
        
        for metric in ['Throughput', 'Goodput', 'Packet Loss Rate', 'Maximum Packet Size']:
            if metric in server_df.columns:
                f.write(f"{metric} Comparison:\n")
                for _, row in server_df.sort_values(['nagle', 'delayed_ack']).iterrows():
                    config = f"Nagle: {'Enabled' if row['nagle'] else 'Disabled'}, " \
                             f"Delayed-ACK: {'Enabled' if row['delayed_ack'] else 'Disabled'}"
                    f.write(f"  {config}: {row[metric]}\n")
                f.write("\n")
        
        # Client-side metrics
        f.write("-"*80 + "\n")
        f.write("CLIENT-SIDE METRICS\n")
        f.write("-"*80 + "\n\n")
        
        for metric in ['Average Rate', 'Average Packet Size', 'Maximum Packet Size']:
            if metric in client_df.columns:
                f.write(f"{metric} Comparison:\n")
                for _, row in client_df.sort_values(['nagle', 'delayed_ack']).iterrows():
                    config = f"Nagle: {'Enabled' if row['nagle'] else 'Disabled'}, " \
                             f"Delayed-ACK: {'Enabled' if row['delayed_ack'] else 'Disabled'}"
                    f.write(f"  {config}: {row[metric]}\n")
                f.write("\n")
        
        # Analysis and observations
        f.write("-"*80 + "\n")
        f.write("ANALYSIS AND OBSERVATIONS\n")
        f.write("-"*80 + "\n\n")
        
        f.write("Effects of Nagle's Algorithm:\n")
        f.write("  Nagle's algorithm aims to reduce network congestion by combining small packets into larger ones.\n")
        f.write("  When enabled, it generally reduces the number of packets while increasing their average size.\n")
        f.write("  This can improve efficiency for bulk transfers but may introduce latency for interactive applications.\n\n")
        
        f.write("Effects of Delayed-ACK:\n")
        f.write("  Delayed-ACK aims to reduce overhead by not immediately acknowledging every packet.\n")
        f.write("  When enabled, it can reduce the number of ACK packets sent, improving efficiency.\n")
        f.write("  However, it can interact with Nagle's algorithm to cause delays in certain scenarios.\n\n")
        
        f.write("Interaction Between Nagle and Delayed-ACK:\n")
        f.write("  When both are enabled, they can create a 'mini-deadlock' situation where:\n")
        f.write("  - Nagle's algorithm waits for enough data or an ACK before sending\n")
        f.write("  - Delayed-ACK waits before sending acknowledgments\n")
        f.write("  This can significantly reduce performance for certain traffic patterns.\n\n")
        
        f.write("Optimal Configuration:\n")
        f.write("  The optimal configuration depends on the application requirements:\n")
        f.write("  - For bulk data transfer: Nagle enabled, Delayed-ACK enabled\n")
        f.write("  - For interactive applications: Nagle disabled, Delayed-ACK varies\n")
        f.write("  - For minimal latency: Both disabled\n\n")
    
    print(f"Comparison report generated: {report_file}")
    
    # Create basic visualization
    try:
        plt.figure(figsize=(12, 8))
        
        # Plot throughput comparison
        if 'Throughput' in server_df.columns:
            #plt.subplot(2, 2, 1)
            configs = []
            for _, row in server_df.iterrows():
                configs.append(f"N:{'On' if row['nagle'] else 'Off'}\nD:{'On' if row['delayed_ack'] else 'Off'}")
            plt.bar(configs, server_df['Throughput'])
            plt.title('Throughput Comparison')
            plt.ylabel('Bytes/sec')
            plt.xticks(rotation=0)
            plt.savefig(f"throughput_comparison.png")
        
        # Plot goodput comparison
        if 'Goodput' in server_df.columns:
            #plt.subplot(2, 2, 2)
            configs = []
            for _, row in server_df.iterrows():
                configs.append(f"N:{'On' if row['nagle'] else 'Off'}\nD:{'On' if row['delayed_ack'] else 'Off'}")
            plt.bar(configs, server_df['Goodput'])
            plt.title('Goodput Comparison')
            plt.ylabel('Bytes/sec')
            plt.xticks(rotation=0)
            plt.savefig(f"goodput_comparison.png")
        # Plot packet loss rate
        if 'Packet Loss Rate' in server_df.columns:
            #plt.subplot(2, 2, 3)
            configs = []
            for _, row in server_df.iterrows():
                configs.append(f"N:{'On' if row['nagle'] else 'Off'}\nD:{'On' if row['delayed_ack'] else 'Off'}")
            plt.bar(configs, server_df['Packet Loss Rate'])
            plt.title('Packet Loss Rate')
            plt.ylabel('Rate')
            plt.xticks(rotation=0)
            plt.savefig(f"packet_loss_rate_comparison.png")
        # Plot maximum packet size
        if 'Maximum Packet Size' in server_df.columns:
            #plt.subplot(2, 2, 4)
            configs = []
            for _, row in server_df.iterrows():
                configs.append(f"N:{'On' if row['nagle'] else 'Off'}\nD:{'On' if row['delayed_ack'] else 'Off'}")
            plt.bar(configs, server_df['Maximum Packet Size'])
            plt.title('Maximum Packet Size')
            plt.ylabel('Bytes')
            plt.xticks(rotation=0)
            plt.savefig(f"maximum_packet_size_comparison.png")
        
        #plt.tight_layout()
        #plt.savefig(f"performance_comparison_{timestamp}.png")
        print(f"Performance visualization saved: performance_comparison_{timestamp}.png")
    except Exception as e:
        print(f"Error creating visualization: {e}")

def main():
    parser = argparse.ArgumentParser(description='Run TCP performance tests with different configurations')
    parser.add_argument('--port-start', type=int, default=8000, help='Starting port number for tests')
    parser.add_argument('--data-size', type=int, default=4096, help='Size of test data in bytes')
    parser.add_argument('--rate', type=int, default=40, help='Data rate in bytes per second')
    parser.add_argument('--duration', type=int, default=120, help='Test duration in seconds')
    parser.add_argument('--report-only', action='store_true', help='Generate report from existing results without running tests')
    
    args = parser.parse_args()
    
    if not args.report_only:
        # Run all four test configurations
        port = args.port_start
        
        # Test 1: Nagle enabled, Delayed-ACK enabled
        run_test(True, True, port, args.data_size, args.rate, args.duration)
        port += 1
        
        # Test 2: Nagle enabled, Delayed-ACK disabled
        run_test(True, False, port, args.data_size, args.rate, args.duration)
        port += 1
        
        # Test 3: Nagle disabled, Delayed-ACK enabled
        run_test(False, True, port, args.data_size, args.rate, args.duration)
        port += 1
        
        # Test 4: Nagle disabled, Delayed-ACK disabled
        run_test(False, False, port, args.data_size, args.rate, args.duration)
    
    # Collect and report results
    server_results, client_results = collect_results()
    generate_report(server_results, client_results)

if __name__ == "__main__":
    main()