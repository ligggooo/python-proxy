import socket
import threading

# Function to handle the connection between the client and the target server
def handle_client(client_socket, remote_host, remote_port):
    # Connect to the remote server
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    # Function to forward data from one socket to another
    def forward(source, destination):
        while True:
            data = source.recv(4096)
            if len(data) == 0:
                break
            destination.sendall(data)

    # Start threads to forward data in both directions
    client_to_remote = threading.Thread(target=forward, args=(client_socket, remote_socket))
    remote_to_client = threading.Thread(target=forward, args=(remote_socket, client_socket))
    client_to_remote.start()
    remote_to_client.start()

    # Wait for both threads to finish
    client_to_remote.join()
    remote_to_client.join()

    # Close the sockets
    client_socket.close()
    remote_socket.close()

# Function to start the proxy server
def start_proxy(local_host, local_port, remote_host, remote_port):
    # Create a socket to listen for incoming connections
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((local_host, local_port))
    server.listen(5)
    print(f"[*] Listening on {local_host}:{local_port}")

    while True:
        # Accept an incoming connection
        client_socket, addr = server.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

        # Start a new thread to handle the connection
        client_handler = threading.Thread(
            target=handle_client,
            args=(client_socket, remote_host, remote_port)
        )
        client_handler.start()

if __name__ == "__main__":
    # Define the local and remote addresses
    LOCAL_HOST = "0.0.0.0"
    LOCAL_PORT = 9999
    REMOTE_HOST = "example.com"
    REMOTE_PORT = 80

    # Start the proxy server
    start_proxy(LOCAL_HOST, LOCAL_PORT, REMOTE_HOST, REMOTE_PORT)