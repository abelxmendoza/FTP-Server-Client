import socket


def main():
    server_host = "127.0.0.1"  # Update with your server's IP address
    server_port = 1200  # Update with your server's port number

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_host, server_port))

    while True:
        response = client.recv(1024).decode()
        print(response)

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


if __name__ == "__main__":
    main()
