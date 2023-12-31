'''
                                              
  ______  ____ _______ ___  __  ____ _______  
 /  ___/_/ __ \\_  __ \\  \/ /_/ __ \\_  __ \ 
 \___ \ \  ___/ |  | \/ \   / \  ___/ |  | \/ 
/____  > \___  >|__|     \_/   \___  >|__|    
     \/      \/                    \/         
                                              

'''



import socket
import os

# Function to list files in the server directory
def list_files():
    files = os.listdir('.')
    return "\n".join(files)

# Function to handle client requests
def handle_client(client_socket):
    welcome_message = "Welcome to the FTP server. Available commands: ls, get <filename>, put <filename>"
    client_socket.send(welcome_message.encode())

    while True:
        request = client_socket.recv(1024).decode()
        if not request:
            break

        if request == "ls":
            file_list = list_files()
            client_socket.send(file_list.encode())
        elif request.startswith("get "):
            filename = request[4:]
            try:
                with open(filename, "rb") as file:
                    client_socket.send(file.read())
            except FileNotFoundError:
                client_socket.send("File not found".encode())
        elif request.startswith("put "):
            filename = request[4:]
            data = client_socket.recv(1024)
            with open(filename, "wb") as file:
                file.write(data)
            client_socket.send("File uploaded successfully".encode())
        else:
            client_socket.send("Invalid command".encode())

    client_socket.close()

# Create a socket and start listening for connections
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 21))
server.listen(5)
print("FTP server listening on port 21")

while True:
    client_socket, addr = server.accept()
    print(f"Accepted connection from {addr}")
    handle_client(client_socket)


