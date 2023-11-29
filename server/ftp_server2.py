import socket
import os
import sys

def list_files():
    files = os.listdir(".")
    return "\n".join(files)

def handle_client(client_socket, data_channel_port):
    # Send welcome message to the client
    welcome_message = "Welcome to the FTP server. Available commands: ls, get <filename>, put <filename>, quit"
    client_socket.send(welcome_message.encode())

    # Establish the data channel for file transfer
    data_channel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_channel.connect(("127.0.0.1", data_channel_port))

    while True:
        # Receive client's command
        request = client_socket.recv(1024).decode()

        if "quit" in request:
            break
        elif request == "ls":
            # Send the list of files to the client
            file_list = list_files()
            client_socket.send(file_list.encode())
        elif request.startswith("get "):
            filename = request[4:]
            # Send the requested file to the client
            send_file(client_socket, filename, data_channel)
        elif request.startswith("put "):
            filename = request[4:]
            # Receive a file from the client
            receive_file(client_socket, filename, data_channel)

    # Close both control and data channels
    client_socket.close()
    data_channel.close()

def send_file(client_socket, filename, data_channel):
    if not os.path.exists(filename):
        # If file not found, send failure message
        client_socket.send(b"FAILURE: File not found")
    else:
        # If file found, send success message and start sending the file
        client_socket.send(b"SUCCESS: File found")
        with open(filename, "rb") as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                data_channel.send(data)

def receive_file(client_socket, filename, data_channel):
    response = client_socket.recv(1024).decode()
    if "FAILURE" in response:
        # If the server indicates failure, print the message
        print(response)
    else:
        # If the server indicates success, receive the file
        with open(filename, "wb") as file:
            while True:
                data = data_channel.recv(1024)
                if not data:
                    break
                file.write(data)
        print(f"SUCCESS: File '{filename}' received on server side")

def main():
    if len(sys.argv) < 3:
        print("ERROR (FORMAT): ftp_server2.py <server ip> <server port>")
        exit(1)

    # Parse command-line arguments
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])

    # Set up the control channel (server socket)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, server_port))
    server.listen(5)
    print(f"SUCCESS: FTP server listening on {server_ip}:{server_port}")

    while True:
        # Accept incoming connections on the control channel
        client_socket, addr = server.accept()
        print(f"SUCCESS: Accepted connection from {addr}")

        # Receive the data channel port from the client
        data_channel_port = int(client_socket.recv(1024).decode())

        # Handle client requests on the control channel
        handle_client(client_socket, data_channel_port)

if __name__ == "__main__":
    main()
