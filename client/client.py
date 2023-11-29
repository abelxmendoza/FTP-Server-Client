import socket
import sys
import os


def create_data_socket():
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.bind(("", 0))  # Bind to an ephemeral port
    return data_socket


def handle_put_command(client, command):
    filename = command[4:]
    if not os.path.exists(filename):
        print("ERROR: File not found")
        return

    data_socket = create_data_socket()
    data_port = data_socket.getsockname()[1]
    client.send(f"DATA_PORT {data_port}".encode())
    data_socket.listen(1)

    data_conn, _ = data_socket.accept()
    with open(filename, "rb") as file:
        data = file.read()
        data_conn.send(data)

    print(f"File {filename} uploaded successfully, {len(data)} bytes transferred.")
    data_conn.close()
    data_socket.close()


def handle_get_command(client, command):
    filename = command[4:]
    data_socket = create_data_socket()
    data_port = data_socket.getsockname()[1]
    client.send(f"DATA_PORT {data_port}".encode())
    data_socket.listen(1)

    data_conn, _ = data_socket.accept()
    data = data_conn.recv(1024)
    if data:
        with open(filename, "wb") as file:
            file.write(data)
        print(
            f"File {filename} downloaded successfully, {len(data)} bytes transferred."
        )

    data_conn.close()
    data_socket.close()


def handle_ls_command(client):
    data_socket = create_data_socket()
    data_port = data_socket.getsockname()[1]
    client.send(f"DATA_PORT {data_port}".encode())
    data_socket.listen(1)

    data_conn, _ = data_socket.accept()
    data = data_conn.recv(1024).decode()
    print(data)

    data_conn.close()
    data_socket.close()


def executeCommands(client):
    while True:
        command = input("Enter a command: ")
        client.send(command.encode())

        if command == "quit":
            return
        elif command.startswith("get "):
            handle_get_command(client, command)
        elif command.startswith("put "):
            handle_put_command(client, command)
        elif command == "ls":
            handle_ls_command(client)


def main():
    if len(sys.argv) < 3:
        print("Usage: ftp_client.py <server ip> <server port>")
        sys.exit(1)

    server_host = sys.argv[1]
    server_port = int(sys.argv[2])

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((server_host, server_port))
    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)

    print(client.recv(1024).decode())  # Welcome message
    executeCommands(client)
    client.close()


if __name__ == "__main__":
    main()
