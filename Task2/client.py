import socket
import time

# Server configuration
HOST = '127.0.0.1'  # Server IP (localhost)
PORT = 1234         # Server port
LOCAL_PORT = 1235  # Local port to use for the client

# Send data to the server
for i in range(100):  # Send 100 messages
    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Set the SO_REUSEADDR option to allow reuse of the local port
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind the client socket to a specific local port
        client_socket.bind(('0.0.0.0', LOCAL_PORT))

        # Connect to the server
        client_socket.connect((HOST, PORT))
        print(f"Connected to server at {HOST}:{PORT} from local port {LOCAL_PORT}")

        # Send the message
        message = f"Message {i+1}"
        client_socket.sendall(message.encode('utf-8'))

        # Wait for the acknowledgment from the server
        #ack = client_socket.recv(1024).decode('utf-8')
        #if ack == "ACK":
        print(f"Sent: {message}")

        # Close the connection
        client_socket.close()
        print("Connection closed")

        # Wait for 0.4 seconds between messages
        time.sleep(0.2)
    except ConnectionResetError:
        print("Connection reset by server")
    except Exception as e:
        print(f"An error occurred: {e}")