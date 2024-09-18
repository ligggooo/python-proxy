import socket
import threading
import urllib.parse


def handle_client(client_socket: socket.socket):
    request_data = client_socket.recv(4096)
    request_lines = request_data.decode().split("\r\n")
    method, url, protocol = request_lines[0].split()
    url_parts = urllib.parse.urlparse(url)
    print(url_parts, method, protocol)
    hostname = url_parts.netloc
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((hostname, 80))
    server_socket.sendall(request_data)
    while True:
        response_data = server_socket.recv(4096)
        if response_data:
            print("==>", response_data.decode())
            client_socket.sendall(request_data)
        else:
            break
    client_socket.close()
    server_socket.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("0.0.0.0", 8888)
    server_socket.bind(server_address)
    server_socket.listen(5)
    print("started at %s %d" % server_address)
    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()


if __name__ == "__main__":
    print("hello")
    main()
