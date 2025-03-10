import matplotlib.pyplot as plt
import numpy as np

# Path to the text file (replace with the actual file path)
file_path = "windowsizes.txt"

# Lists to store timestamps and cwnd values
timestamps = []
cwnd_values = []

# Read the file and extract data
with open(file_path, "r") as file:
    for line in file:
        if "sec" in line and "KBytes" in line:  # Ensure it's a line containing time and cwnd info
            #print("Hi" )
            try:
                # Example line format: [  5]   0.00-1.00   sec  1.25 MBytes  10.5 Mbits/sec    0    165 KBytes
                parts = line.split()
                print(parts)
                # Extract the time range (e.g., 0.00-1.00)
                time_range = parts[2]
                start_time = float(time_range.split('-')[0])  # Use the start time
                
                # Extract the cwnd value (last item in the line, e.g., 165 KBytes)
                cwnd_str = parts[-2]  # '165 KBytes'
                #cwnd_value = int(cwnd_str.replace('KBytes', '').strip()) * 1024  # Convert KBytes to bytes
                
                timestamps.append(start_time)
                cwnd_values.append(float(cwnd_str))
            except Exception as e:
                continue  # If something goes wrong, skip this line

# Convert to numpy arrays for better processing
timestamps = np.array(timestamps[0:len(cwnd_values)])
cwnd_values = np.array(cwnd_values)

# Find the maximum cwnd value and its corresponding timestamp
max_cwnd = np.max(cwnd_values)
max_cwnd_time = timestamps[np.argmax(cwnd_values)]

# Scatter plot of cwnd vs time
plt.figure(figsize=(10, 6))
plt.scatter(timestamps, cwnd_values, label="Congestion Window (cwnd)", color='blue', s=10)

# Mark the largest cwnd
#plt.scatter(max_cwnd_time, max_cwnd, color='red', label=f"Max cwnd = {max_cwnd / 1024:.2f} KB", s=50)
#plt.axvline(x=max_cwnd_time, color='red', linestyle='--', label=f"Max cwnd at {max_cwnd_time:.2f}s")

# Labels and title
plt.xlabel('Time (seconds)')
plt.ylabel('Congestion Window Size (bytes)')
plt.title('Scatter Plot of cwnd (Congestion Window Size) vs Time')
plt.legend()
plt.grid(True)

# Show the plot
plt.tight_layout()
plt.show()
