import socket
import sys
import os

LOCALHOST_IP_ADDRESS = "127.0.0.1"

# create ephemeral port
def create_data_channel_socket():
    data_channel_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_channel_socket.bind((LOCALHOST_IP_ADDRESS, 0))
    data_channel_socket.listen(5)
    return [data_channel_socket, data_channel_socket.getsockname()[1]]

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
    size_of_data_message = socket.recv(10).decode()
    data_size = 0
    recover_data_size = extract_data_size(size_of_data_message)
    while data_size < recover_data_size:
        chunk = socket.recv(40).decode()
        data += chunk
        data_size += len(chunk)
    return data

def set_up_data(data):
    data_size = str(len(data))
    new_data = data_size + '*' * (10 - len(data_size)) + data
    return new_data

def sent_data(socket, data):
    byteSent = 0
    modified_data = set_up_data(data)
    while byteSent != len(modified_data):
        byteSent += socket.send(modified_data[byteSent:].encode())

def connect_server_to_data_socket(client_control_channel_socket):
    socket_info = create_data_channel_socket()
    data_channel_socket = socket_info[0]
    data_channel_socket_port = socket_info[1]
    
    sent_data(client_control_channel_socket, data=str(data_channel_socket_port))
    while True:
        try:
            server_socket_info = data_channel_socket.accept()
            if server_socket_info:
                server_socket = server_socket_info[0]
                break
        except Exception as error:
            print("Error during accept connection: " + error)
            continue
    
    return [data_channel_socket, server_socket]

def executeCommands(client_control_channel_socket):
    command = input("Enter a command: ")

    if command == "quit":
        sent_data(client_control_channel_socket, command)
        print("Exit the control channel connection")
        return False
    
    elif command.startswith("get "): # get data from server
        filename = command[4:]

        #send command to server
        sent_data(client_control_channel_socket, command)
        server_signal_message = recover_data(client_control_channel_socket)

        # If the file requested already exits in client's folder
        if os.path.exists(filename):
            answer = input("File: " + filename + " already exist in current folder. Want to override the existed file with the new file? (Y/N)")
            if answer == 'N':
                server_signal_message = "FAILURE"

        # Server is ready to connect to data_channel_socket
        if server_signal_message == "READY":
            data_channel_socket, server_socket = connect_server_to_data_socket(client_control_channel_socket)
            file_data = recover_data(server_socket)
            data_channel_socket.close()

            try:
                with open(filename, "wb") as file:
                    file.write(file_data.encode('utf-8'))
            except OSError as error:
                print("ERROR: Can't write file data to a file, error: " + error + "\n")
                sent_data(client_control_channel_socket, "FAILURE")
            else:
                sent_data(client_control_channel_socket, "SUCCESS")
                print("STATUS: Received data file from server")
                print("Total data transferred: " + str(len(file_data)) + " bytes\n")

        elif server_signal_message == "FAILURE":
            print("STATUS: Server unable to sent file data to client\n")

    elif command.startswith("put "):  # put data from client to server
        filename = command[4:]

        # File does not exist in client
        if not os.path.exists(filename):
            print("File: " + filename + " doesn't exist in current directory\n")
        else:
            #send command to server
            sent_data(client_control_channel_socket, command)
            server_signal_message = recover_data(client_control_channel_socket)

            # Server is ready to connect to data_channel_socket
            if server_signal_message == "READY":
                data_channel_socket, server_socket = connect_server_to_data_socket(client_control_channel_socket)
                with open(filename, "rb") as file:
                    file_data = file.read()
                    sent_data(server_socket, file_data.decode())
                    data_channel_socket.close()

                #get response from server                   
                server_response = recover_data(client_control_channel_socket)
                if server_response == "SUCCESS":
                    print("STATUS: Server succfessfully received file")
                    print("Total data transferred: " + str(len(file_data.decode())) + " bytes\n")
                if server_response == "FAILURE":
                    print("STATUS: Server unsuccessfully received file\n")

            # The file sent by client already exist in server
            elif server_signal_message == "FAILURE":
                print("STATUS: Server unsuccessfully received file\n")
    
    elif command == "ls":
        #send command to server
        sent_data(client_control_channel_socket, command)
        server_signal_message = recover_data(client_control_channel_socket)

        # Server is ready to connect to data_channel_socket
        if server_signal_message == "READY":
            data_channel_socket, server_socket = connect_server_to_data_socket(client_control_channel_socket)

        # Receive data from data channel
        recovered_data = recover_data(server_socket)
        data_channel_socket.close()
        print("STATUS: Received list of files from server")

        #send confirmation that client received all the data
        sent_data(client_control_channel_socket, "SUCCESS")

        print(recovered_data)
        print("Total data transferred: " + str(len(recovered_data)) + " bytes\n")

    return True


def main():
    
    if len(sys.argv) < 3:
        print("ERROR (FORMAT): ftp_client.py <server ip> <server port>")
        exit(1)
    server_control_host = sys.argv[1]  # Update with your server's IP address
    server_control_port = int(sys.argv[2])  # Update with your server's port number
    run = True

    client_control_channel_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Client tries to connect to server.
    try:
        client_control_channel_socket.connect((server_control_host, server_control_port))
    except InterruptedError:
        print(InterruptedError)
    else:
        data = recover_data(client_control_channel_socket)
        print(data)

    while run:
        run = executeCommands(client_control_channel_socket)

    client_control_channel_socket.close()

if __name__ == "__main__":
    main()
