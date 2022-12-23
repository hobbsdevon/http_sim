# Code for UDP implementation of HTTP
# 15 December 2022
# Author: Devon Hobbs

import socket
import time
import os

# SOCK_DGRAM must be used for a UDP connection
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Socket successfully created")

PORT = 8180
BUFFERSIZE = 1024
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
REQUEST_TYPES = ['GET', 'PUT', 'POST', 'DELETE', 'HEAD']

s.bind(('', PORT))
print("socket bound to %s" % PORT)


def start_server():
    while True:
        # receive incoming data
        addr, msg, req_type = parse_packet()

        print(msg)
        s.sendto(service_request(req_type, msg), addr)


def create_response(resp_type, body=''):
    # dictionary to keep track of the response types
    resp_dict = {'400': 'Bad_Request',
                 '301': 'Moved_Permanently',
                 '404': 'Not_Found',
                 '200': 'OK',
                 '505': 'HTTP_Version_Not_Supported'}

    response = 'HTTP\\1.1' + ' ' + resp_type + ' ' + str(resp_dict[resp_type] + '\n' +
                                                         'Time: ' + time.strftime("%H:%M:%S",
                                                                                  time.localtime()) + '\n\n' + body)
    return response


# method to create the response for a GET request
def get_response(msg):
    file_name = msg.split(' ')[1]
    if os.path.isfile(file_name):
        f = open(file_name, "rb")
        file_data = f.read(BUFFERSIZE)
        response = create_response('200').encode(FORMAT)
        response += file_data
        f.close()
    else:
        response = create_response('404').encode(FORMAT)
    return response


def put_response(msg):
    file_name = msg.split(' ')[1]
    body_start = msg.find('\n\n')
    file_contents = msg[body_start + 1:]
    f = open(file_name, 'wb')
    f.write(file_contents)
    f.close()
    response = create_response('200').encode(FORMAT)
    return response


def post_response(msg):
    post_msg = msg.split('\n')[-1]
    print('post: ', post_msg)
    response = create_response('200').encode(FORMAT)
    return response


def delete_response(msg):
    file_name = msg.split(' ')[1]
    if os.path.isfile(file_name):
        os.remove(file_name)
        response = create_response('200').encode(FORMAT)
    else:
        response = create_response('404').encode(FORMAT)
    return response


def service_request(req_type, msg):
    # disconnects immediately if disconnect message is sent
    if msg == DISCONNECT_MESSAGE:
        s.close()
        exit()
    # goes through request types
    http_version = msg.split(' ')[2].split('\n')[0]
    if http_version != 'HTTP\\1.1':
        response = create_response('505').encode(FORMAT)
    elif req_type == 'GET':
        response = get_response(msg)
    elif req_type == 'PUT':
        response = put_response(msg)
    elif req_type == 'POST':
        response = post_response(msg)
    elif req_type == 'DELETE':
        response = delete_response(msg)
    elif req_type == 'HEAD':
        response = create_response('200').encode(FORMAT)
    else:
        response = create_response('400').encode(FORMAT)

    return response


def parse_packet():
    data, addr = s.recvfrom(BUFFERSIZE)
    msg = data.decode(FORMAT)
    req_type = msg.split(' ')[0].upper()
    return addr, msg, req_type


start_server()