import socket

def connect_to_server(host, port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        return client_socket
    except socket.error as e:
        print(f"Error connecting to the server: {e}")
        return None

def receive_data(socket):
    try:
        return socket.recv(1024).decode()
    except socket.error as e:
        print(f"Error receiving data: {e}")
        return None

def send_data(socket, data):
    try:
        socket.send(data.encode())
    except socket.error as e:
        print(f"Error sending data: {e}")

def receive_file(socket, filename):
    try:
        with open(filename, "wb") as file:
            while True:
                data = socket.recv(1024)
                if not data:
                    break
                file.write(data)
    except IOError as e:
        print(f"Error writing file: {e}")
    except socket.error as e:
        print(f"Error receiving file data: {e}")

def send_file(socket, filename):
    try:
        with open(filename, "rb") as file:
            data = file.read(1024)
            while data:
                socket.send(data)
                data = file.read(1024)
    except IOError as e:
        print(f"Error reading file: {e}")
    except socket.error as e:
        print(f"Error sending file data: {e}")

def main():
    server_host = '127.0.0.1'
    server_port = 21

    client = connect_to_server(server_host, server_port)

    if client is None:
        print("Unable to establish a connection. Exiting.")
        return

    while True:
        response = receive_data(client)
        if response is None:
            break
        print(response)

        command = input("Enter a command: ")
        send_data(client, command)

        if command == "quit":
            break
        elif command.startswith("get "):
            filename = command[4:]
            receive_file(client, filename)
        elif command.startswith("put "):
            filename = command[4:]
            send_file(client, filename)
        elif command == "ls":
            file_list = receive_data(client)
            if file_list is not None:
                print(file_list)

    client.close()

if __name__ == '__main__':
    main()
