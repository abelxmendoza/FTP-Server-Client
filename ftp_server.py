import socket
import os
import sys

LOCALHOST_IP_ADDRESS = "127.0.0.1"

# Function to list files in the server directory
def list_files():
    files = os.listdir(".")
    return "\n".join(files)

# Function to handle client requests
def handle_client(client_control_channel_socket):
    while True:
        # server recovers client's command
        request = recover_data(client_control_channel_socket)

        if "quit" in request:
            print("Client exit the connection")
            break
        if request == "ls":
            data = "READY"
            send_data(client_control_channel_socket, data)
            data_channel_port = recover_data(client_control_channel_socket)
            data_channel_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                data_channel_socket.connect((LOCALHOST_IP_ADDRESS, int(data_channel_port)))
            except InterruptedError as error:
                print("FAILED: " + error)
            else:
                file_list = list_files()
                print("Client requested command: ls")
                send_data(data_channel_socket, file_list)
                client_result_response = recover_data(client_control_channel_socket)

                if client_result_response == "SUCCESS":
                    print("SUCCESS: Client received a list of files")
                else:
                    print("FAILURE: Client didn't received the list of files")
            data_channel_socket.close()

        elif request.startswith("get "):
            filename = request[4:]
            try:
                file = open(filename, "rb")
            except FileNotFoundError:
                client_control_channel_socket.send("FAILURE: File not found".encode())
                send_data(client_control_channel_socket, "FAILURE")
            else:
                send_data(client_control_channel_socket, "READY")
                data_channel_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                data_channel_port = recover_data(client_control_channel_socket)

                try:
                    data_channel_socket.connect((LOCALHOST_IP_ADDRESS, int(data_channel_port)))
                except InterruptedError as error:
                    print("FAILURE: " + error)
                else:
                    data_file = file.read()
                    send_data(data_channel_socket, data_file.decode())
                    client_response = recover_data(client_control_channel_socket)
            data_channel_socket.close()
                
            if client_response == "SUCCESS":
                print("SUCCESS: Client received data file")
            elif client_response == "FAILURE":
                print("FAILURE: Client didn't received data file")

        elif request.startswith("put "):
            filename = request[4:]
            print("Client requested command: put")

            if os.path.exists(filename):
                print("FAIlURE: File's name sent from client already exist in server's foulder")
                send_data(client_control_channel_socket, "FAILURE")
            else:
                send_data(client_control_channel_socket, "READY")
                data_channel_port = recover_data(client_control_channel_socket)
                data_channel_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                try:
                    data_channel_socket.connect((LOCALHOST_IP_ADDRESS, int(data_channel_port)))
                except InterruptedError as error:
                    print("FAILURE: " + error)
                else:
                    file_data = recover_data(data_channel_socket)
                    try:
                        with open(filename, "wb") as file:
                            file.write(file_data.encode('utf-8'))
                    except OSError as error:
                        send_data(client_control_channel_socket, "FAILURE")
                        print("FAIlURE: " + error)
                    else:
                        send_data(client_control_channel_socket, "SUCCESS")
                        print("SUCCESS: Server received file from client")
            data_channel_socket.close()

    return False

# Get data size of the actual data
def extract_data_size(data):
    data_size = ""
    for i in range(len(data)):
        if data[i] == "*":
            break
        else:
            data_size += data[i]
    return int(data_size)

def recover_data(socket):
    data = ""
    size_of_data_message = socket.recv(10).decode() #First 10 bytes contains the size of data
    data_size = 0
    recover_data_size = extract_data_size(size_of_data_message)
    while data_size < recover_data_size:
        chunk = socket.recv(40).decode()
        data += chunk
        data_size += len(chunk)
    return data

#Add the total number of byte of data to the data
def set_up_data(data):
    data_size = str(len(data))
    new_data = data_size + '*' * (10 - len(data_size)) + data
    return new_data

def send_data(socket, data):
    byteSent = 0
    modified_data = set_up_data(str(data))
    while byteSent != len(modified_data):
        byteSent += socket.send(modified_data[byteSent:].encode())

def main():
    if len(sys.argv) < 2:  # Use port number 1200
        print("ERROR (FORMAT): ftp_server.py <server port>")
        exit(1)

    control_port = int(sys.argv[1])
    welcome_message = "Welcome to the FTP server. Available commands: ls, get <filename>, put <filename>, quit"
    run_control_channel = True

    # Create a control_channel socket and start listening for connections
    control_channel_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_channel_socket.bind((LOCALHOST_IP_ADDRESS, control_port))
    control_channel_socket.listen(5)
    print(f"FTP server listening on port {control_port}")

    message = str("Connected to server at Port: " + str(control_port) + "\n" + welcome_message)

    while run_control_channel:
        try:
            client_control_channel_socket, client_addr = control_channel_socket.accept()
        except InterruptedError as error:
            print("FAILED: Can't accept client connection to control channel, error: " + str(error))
        else:
            print("Accepted connection from " + str(client_addr))
            send_data(client_control_channel_socket, message)

        run_control_channel = handle_client(client_control_channel_socket)

    control_channel_socket.close()

if __name__ == "__main__":
    main()
