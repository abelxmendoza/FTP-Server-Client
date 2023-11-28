import socket
import sys


def executeCommands(client):
    command = input("Enter a command: ")
    client.send(command.encode())

    if command == "quit":
        return False
    elif command.startswith("get "): # get data from server
        filename = command[4:]
        data = client.recv(1024)

        # If data file not found, send error message
        if data.decode() == "File not found":
            print(data.decode())

        else:
            with open(filename, "wb") as file:
                file.write(data)

    elif command.startswith("put "): # put data from client to server
        filename = command[4:]
        with open(filename, "rb") as file:
            data = file.read()
            client.send(data) # client send data to server
            print(client.recv(1024).decode()) # client recovers response from server
    elif command == "ls":
        file_list = client.recv(1024).decode()
        print(file_list)

    return True


def main():
    if len(sys.argv) < 3:
        print("ERROR (FORMAT): ftp_client.py <server ip> <server port>")
        exit(1)

    server_host = sys.argv[1]  # Update with your server's IP address
    server_port = int(sys.argv[2])  # Update with your server's port number
    run = True

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Client tries to connect to server.
    try:
        client.connect((server_host, server_port))
    except InterruptedError:
        print(InterruptedError)
    else:
        # Server initial response should be 
        # "Welcome to the FTP server. Available commands: ls, get <filename>, put <filename>, quit"
        response = client.recv(1024).decode()
        print(response)

    while run:
        run = executeCommands(client)

    client.close()

if __name__ == "__main__":
    main()
