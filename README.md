# CS331_Assign2

Aayush Parmar 22110181  
Bhoumik Patidar 22110049

The repository has three folder for the three tasks.

**TASK1**

To run the files use 
```
sudo python3 topo_a.py
```
and 
```
ryu-manager ryu.app.simple_switch_13
``` 
on another terminal to turn on the remote controller.

Further mininet CLI includes
```
h7 xterm -title "H7 Server" -e "iperf3 -s -p 5001; bash" &
```
and 
```

h1 xterm -title "H1 Client (Cubic)" -e "iperf3 -c 10.0.0.7 -p 5001 -b 10M -P 10 -t 150 -i 1 -Z cubic; bash" &
```

**TASK2**

Start server and client programs on separate terminals. Use the below command to capture the packets transfered.
```
sudo tcpdump -i lo -w syn_flood.pcap
```
and use below command to start flooding the server
```
sudo hping3 -S -p 1234 --flood 127.0.0.1
```

**TASK3**

Run the Task 3 using 
```
sudo python3 runner.py
```