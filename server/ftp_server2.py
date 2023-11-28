import socket
import os

def list_files():
    try:
        files = os.listdir('.')
        return "\n".join(files)
    except OSError as e:
        print(f"Error listing files: {e}")
        return "Error listing files"

def handle_client(client_socket):
    welcome_message = "Welcome to the FTP server. Available commands: ls, get <filename>, put <filename>"
    send_data(client_socket, welcome_message)

    while True:
        request = receive_data(client_socket)
        if not request:
            break

        if request == "ls":
            file_list = list_files()
            send_data(client_socket, file_list)
        elif request.startswith("get "):
            filename = request[4:]
            send_file(client_socket, filename)
        elif request.startswith("put "):
            filename = request[4:]
            receive_file(client_socket, filename)
        else:
            send_data(client_socket, "Invalid command")

    client_socket.close()

def start_server():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 21))
        server.listen(5)
        print("FTP server listening on port 21")

        while True:
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr}")
            handle_client(client_socket)

    except socket.error as e:
        print(f"Socket error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        server.close()

if __name__ == '__main__':
    start_server()

