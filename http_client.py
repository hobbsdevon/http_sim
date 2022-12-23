# Client side code for UDP implementation of HTTP using sockets
# This version is without large file transfers
# 15 December 2022
# Author: Brodie McCuen

import socket
import os

HEADER = 64
FORMAT = 'utf-8'
BUFFER_SIZE = 2048
DISCONNECT_MESSAGE = '!DISCONNECT'
SERVER_IP = "[insert server ip here]"         # set to whatever IP we want to connect to
SERVER_PORT = 8180
SERVER_ADDR = (SERVER_IP, SERVER_PORT)

# creates format for HTTP request
# just creating one long string
def create_request(req_type, URL, version):
    '''
    This function creates an HTTP request.
    '''

    message = req_type + ' ' + URL + ' ' + version + '\n'
    message = message + "HostName: cornellcollege.edu\n"
    data = ''  
    # if no data is made it just is empty string
    
    if req_type.upper() == 'POST':
        data = input("What would you like to post?: ")
        message = message + "DataType: String\n"

    elif req_type.upper() == 'DELETE':
        pass

    elif req_type.upper() == 'PUT':
        file_name = input("What file would you like to give?: ")

        # checks to see if the file is in directory
        while not os.path.isfile(file_name):
            file_name = input("What file would you like to give?: ")


        f = open(file_name, "r")
        extension = os.path.splitext(file_name)[-1].lower()
        data = f.read(BUFFER_SIZE)
        print(data)
        f.close()
        message = message + "Content-type: " + extension + '\n'
        message = message + "Content-length: 16" + '\n'

    # another new line for the HTTP format
    # body of the request after two new
    message = message + '\n'
    message = message + data
        
    return message


def put_request(message):
    file_name = input("What file would you like to give?: ")

    while not os.path.isfile(file_name):
        file_name = input("What file would you like to give?: ")

    f = open(file_name, "r")
    extension = os.path.splitext(file_name)[-1].lower()
    data = f.read(BUFFER_SIZE)
    f.close()
    message = message + "Content-type: " + extension + '\n'
    message = message + "Content-length: 16" + '\n'

# encodes message and sends message with message length with socket.send()
# message type is string
def send_message(msg, client_socket):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    msg_length = str(msg_length).encode(FORMAT)
    msg_length += b' ' * (HEADER - len(msg_length))
    client_socket.sendto(message, SERVER_ADDR)

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        url = ''
        req_type = input("What Type (GET, POST, DELETE, PUT, HEAD) or type quit to exit: ")
        if req_type == 'quit':
            break

        if req_type == 'GET':
            url = input("What file do you want?: ")
        elif req_type == 'DELETE':
            url = input("What file do you want to delete?: ")
        elif req_type == 'PUT':
            url = input("Where would you like to PUT?: ")
        else:
            url = "cornellcollege.edu"

        http_version = "HTTP\\" + input("Which HTTP version? (1.1 is recommended): ") # bare bones way of getting HTTP data

        msg = create_request(req_type, url, http_version)
        send_message(msg, client_socket)

        # recieves all data from server
        # could be many types of responses with or without a body
        data, addr = client_socket.recvfrom(BUFFER_SIZE)

        data = data.split(b'\n\n', 1)
        header = data[0]
        body = data[1]
        #index = data.find(b'\n\n')
        #header = data[0:index]
        #body = data[index+2:]
        print(body)
        header = header.decode(FORMAT)

        # only for GET requests that are successful
        if req_type == 'GET' and header.split(' ')[1] == '200': 
            
            file_name = url

            f = open(file_name, 'wb')
            f.write(body)
            f.close()
        
        
        print(data)

    send_message(DISCONNECT_MESSAGE, client_socket)
    client_socket.close()
    print("Sending Disconnect")

start_client()