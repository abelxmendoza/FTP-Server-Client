import socket
import os
import sys


# Function to list files in the server directory
def list_files():
    files = os.listdir(".")
    return "\n".join(files)


# Function to handle client requests
def handle_client(client_socket):
    welcome_message = "Welcome to the FTP server. Available commands: ls, get <filename>, put <filename>, quit"
    client_socket.send(welcome_message.encode())

    while True:

        #server recovers client's command
        request = client_socket.recv(1024).decode()

        if "quit" in request:
            break
        if request == "ls":
            file_list = list_files()
            client_socket.send(file_list.encode())
        elif request.startswith("get "):
            filename = request[4:]

            # TODO: New error: If enter a file that doesn't exist in the server folder, 
            # the code some how create that new file then send that to the client
            # when the server should have send an error message to the client
            try:
                with open(filename, "rb") as file:
                    client_socket.send(file.read())
            except FileNotFoundError:
                client_socket.send("File not found".encode())
            #####################################################

        elif request.startswith("put "):
            filename = request[4:]
            data = client_socket.recv(1024)
            with open(filename, "wb") as file:
                file.write(data)
            client_socket.send("File uploaded successfully".encode())
        else:
            client_socket.send("Invalid command".encode())

    client_socket.close()


def main():
    if len(sys.argv) < 2: # Use port number 1200
        print("ERROR (FORMAT): ftp_server.py <server port>")
        exit(1)

    server_port = int(sys.argv[1])
    # Create a socket and start listening for connections
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", server_port))
    server.listen(5)
    print(f"FTP server listening on port {server_port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        handle_client(client_socket)


if __name__ == "__main__":
    main()
