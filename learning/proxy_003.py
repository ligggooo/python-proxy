import socket
import threading
import select

# Function to handle the connection between the client and the target server
def handle_client(client_socket):
    request = client_socket.recv(4096)

    # Parse the request to get the target server and port
    first_line = request.split(b'\n')[0]
    url = first_line.split(b' ')[1]

    http_pos = url.find(b'://')
    if http_pos == -1:
        temp = url
    else:
        temp = url[(http_pos + 3):]

    port_pos = temp.find(b':')

    # Find the end of the web server
    webserver_pos = temp.find(b'/')
    if webserver_pos == -1:
        webserver_pos = len(temp)

    webserver = ""
    port = -1
    if port_pos == -1 or webserver_pos < port_pos:
        port = 80
        webserver = temp[:webserver_pos]
    else:
        port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
        webserver = temp[:port_pos]

    # Create a socket to connect to the target server
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.connect((webserver, port))
    proxy_socket.send(request)

    # Function to forward data from one socket to another
    def forward(source, destination):
        while True:
            data = source.recv(4096)
            if len(data) == 0:
                break
            destination.sendall(data)

    # Start threads to forward data in both directions
    client_to_proxy = threading.Thread(target=forward, args=(client_socket, proxy_socket))
    proxy_to_client = threading.Thread(target=forward, args=(proxy_socket, client_socket))
    client_to_proxy.start()
    proxy_to_client.start()

    # Wait for both threads to finish
    client_to_proxy.join()
    proxy_to_client.join()

    # Close the sockets
    client_socket.close()
    proxy_socket.close()

# Function to start the proxy server
def start_proxy(local_host, local_port):
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
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    # Define the local address
    LOCAL_HOST = "0.0.0.0"
    LOCAL_PORT = 8888

    # Start the proxy server
    start_proxy(LOCAL_HOST, LOCAL_PORT)