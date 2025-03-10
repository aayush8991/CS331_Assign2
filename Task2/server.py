import socket

# Server configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 1234       # Port to listen on

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)  # Allow up to 5 pending connections

print(f"Server listening on {HOST}:{PORT}")

while True:
    # Accept a new connection
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

    # Handle the client
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Received: {data.decode('utf-8')}")
            #client_socket.sendall("ACK".encode('utf-8'))  # Echo back the received data
    except ConnectionResetError:
        print(f"Connection with {client_address} reset by peer")
    finally:
        client_socket.close()
        print(f"Connection with {client_address} closed")