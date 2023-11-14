import socket
import sys


def executeCommands(client):
    command = input("Enter a command: ")
    client.send(command.encode())

    if command == "quit":
        return False
    elif command.startswith("get "):
        filename = command[4:]
        data = client.recv(1024)
        with open(filename, "wb") as file:
            file.write(data)
    elif command.startswith("put "):
        filename = command[4:]
        with open(filename, "rb") as file:
            data = file.read()
            client.send(data)
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
        response = client.recv(1024).decode()
        print(response)

    while run:
        run = executeCommands(client)

    client.close()


"""
        command = input("Enter a command: ")
        client.send(command.encode())

        if command == "quit":
            break
        elif command.startswith("get "):
            filename = command[4:]
            data = client.recv(1024)
            with open(filename, "wb") as file:
                file.write(data)
        elif command.startswith("put "):
            filename = command[4:]
            with open(filename, "rb") as file:
                data = file.read()
                client.send(data)
        elif command == "ls":
            file_list = client.recv(1024).decode()
            print(file_list)

        client.close()
"""

if __name__ == "__main__":
    main()
