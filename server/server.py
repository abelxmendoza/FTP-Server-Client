import socket
import os
import sys


def list_files():
    return "\n".join(os.listdir("."))


def handle_client(client_socket, addr):
    client_socket.send(
        "Welcome to the FTP server. Available commands: ls, get <filename>, put <filename>, quit".encode()
    )

    while True:
        request = client_socket.recv(1024).decode()
        if "quit" in request:
            break

        if "DATA_PORT" in request:
            data_port = int(request.split()[1])
            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_socket.connect(
                (addr[0], data_port)
            )  # addr[0] is the client IP address

            if request.startswith("put "):
                filename = request[4:].split()[0]
                data = data_socket.recv(1024)
                with open(filename, "wb") as file:
                    file.write(data)
                client_socket.send("SUCCESS: File uploaded successfully".encode())

            elif request.startswith("get "):
                filename = request[4:].split()[0]
                try:
                    with open(filename, "rb") as file:
                        data_socket.send(file.read())
                    client_socket.send("SUCCESS: File downloaded successfully".encode())
                except FileNotFoundError:
                    client_socket.send("FAILURE: File not found".encode())

            elif request == "DATA_PORT ls":
                file_list = list_files()
                data_socket.send(file_list.encode())
                client_socket.send("SUCCESS: File list sent".encode())

            data_socket.close()

    client_socket.close()


def main():
    if len(sys.argv) < 2:
        print("Usage: ftp_server.py <server port>")
        sys.exit(1)

    server_port = int(sys.argv[1])
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", server_port))
    server.listen(5)

    print(f"FTP server listening on port {server_port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        handle_client(client_socket, addr)


if __name__ == "__main__":
    main()
