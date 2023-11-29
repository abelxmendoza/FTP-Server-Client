import socket
import sys
import os

def executeCommands(client, data_channel):
    command = input("ftp> ")
    client.send(command.encode())

    if command == "quit":
        return False
    elif command.startswith("get "):
        filename = command[4:]
        receive_file(client, filename, data_channel)
    elif command.startswith("put "):
        filename = command[4:]
        send_file(client, filename, data_channel)
    elif command == "ls":
        receive_ls(client)

    return True

def receive_file(client, filename, data_channel):
    response = client.recv(1024).decode()
    if response == "File not found":
        print(response)
    else:
        with open(filename, "wb") as file:
            while True:
                data = data_channel.recv(1024)
                if not data:
                    break
                file.write(data)
            print(f"SUCCESS: File '{filename}' received")

def send_file(client, filename, data_channel):
    if not os.path.exists(filename):
        print(f"FAILURE: File '{filename}' not found")
        client.send(b"FAILURE")
    else:
        client.send(b"SUCCESS")
        with open(filename, "rb") as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                data_channel.send(data)
        print(f"SUCCESS: File '{filename}' sent")

def receive_ls(client):
    file_list = client.recv(1024).decode()
    print("Server Files:\n", file_list)

def main():
    if len(sys.argv) < 3:
        print("ERROR (FORMAT): ftp_client.py <server ip> <server port>")
        exit(1)

    server_host = sys.argv[1]
    server_port = int(sys.argv[2])

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_channel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((server_host, server_port))
        data_channel.bind(("127.0.0.1", 0))  # Bind to an available port
        data_channel.listen(1)
        client.send(str(data_channel.getsockname()[1]).encode())  # Send the data channel port to the server
        data_connection, _ = data_channel.accept()  # Accept the connection on the data channel
    except Exception as e:
        print(f"ERROR: {e}")
        client.close()
        data_channel.close()
        exit(1)

    response = client.recv(1024).decode()
    print(response)

    run = True
    while run:
        run = executeCommands(client, data_connection)

    client.close()
    data_channel.close()

if __name__ == "__main__":
    main()

