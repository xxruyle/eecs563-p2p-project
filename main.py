import os
import socket
import threading
from random import randint

from auth import *

'''
My p2p protocol  
(client action|filename)
client sending files to tracker (SEND|FILENAME|client addr it will listen on|client port it will listen on)
client requesting files from tracker (REQUEST|FILENAME)

client asking for online client info (CLIENTS|ALL)

client receiving file info from TRACKER (EXISTS|p2p server info)
client receiving file info from TRACKER (NOFILE|p2p server info)
'''

MAX_FILE_SIZE = 8192 


TRACKER_ADDR = "0.0.0.0" 
TRACKER_PORT = 12345

def handle_client(connection, sender_username):
    while True:
        filename = connection.recv(MAX_FILE_SIZE).decode('utf-8')
        if not filename:
            # print("ERROR: No file... breaking") 
            break
        if os.path.exists(filename):
            connection.send(str(os.path.getsize(filename)).encode('utf-8'))
            with open(filename,'rb') as f:
                bytes_read = f.read(MAX_FILE_SIZE)
                while bytes_read:
                    connection.send(bytes_read)
                    bytes_read = f.read(MAX_FILE_SIZE)
            print(f"Sent: {filename}")
        else:
            connection.send(b"The file does not exist")

    connection.close()

def start_tracker(host=TRACKER_ADDR,port=TRACKER_PORT):
    online_clients = {}
    def add_online_client(listening_address, listening_port):
        if listening_address not in online_clients: 
            online_clients[listening_address] = listening_port 

    def remove_online_client(listening_address, listening_port):
        if listening_address in online_clients: 
            del online_clients[listening_address]

    def get_all_online_clients() -> str: 
        send_string = ""
        for addr in online_clients: 
            port = online_clients[addr]
            client_info = f"{addr}:{port}|"
            send_string += client_info

        return send_string 


    file_db = {} # {filename: (peer ip, peer port)}

    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind((host,port))
    sock.listen(5)
    print(f"TRACKER: Listening on {host}:{port}")
    while True:
        conn, addr = sock.accept()
        print(f"TRACKER: Connected by {addr}")
        protocol = conn.recv(MAX_FILE_SIZE).decode('utf-8').split("|") 
        # print(protocol)
        if len(protocol) > 1:
            if protocol[0] == "SEND": 
                filename = protocol[1] 
                listening_addr = protocol[2] 
                listening_port = protocol[3] 
                print(f"TRACKER: received client send data: {filename} - FROM: {(listening_addr, listening_port)}") 
                # store file data and peer info in file_db
                if filename not in file_db: 
                    add_online_client(listening_addr, listening_port)
                    file_db[filename] = (listening_addr, listening_port)
                    print(f"TRACKER: stored sent {filename} in tracker db FROM {(listening_addr, listening_port)}")
                else: 
                    print("TRACKER ERROR: FILE ALREADY EXISTS") 
            elif protocol[0] == "REQUEST": 
                filename = protocol[1]
                print(f"TRACKER: received client request: {filename} - FROM: {addr}") 
                if filename in file_db: 
                    print(f"TRACKER: {filename} exists")
                    p2p_server_addr, p2p_server_port = file_db[filename] 
                    conn.send(f"EXISTS|{p2p_server_addr}|{p2p_server_port}".encode('utf-8'))
                else: 
                    conn.send(f"NOFILE|none".encode('utf-8'))
                    print("TRACKER: FILE DOES NOT EXIST")  
            elif protocol[0] == "CLIENTS":
                clients = get_all_online_clients()
                conn.send(clients.encode('utf-8'))
                print(f"TRACKER: SENDING CLIENT INFO TO {addr}")


        else: 
            print("TRACKER ERROR: invalid protocol format received from client: ", addr)

def client_send_to_tracker(host='127.0.0.1', port=6000, filename='', username=''): 
    '''
        - Client sends the name of file that it wants to share and its connection information to the
        Tracker node.
        – The client then opens a socket and wait for requests from other peers for a file that it
        holds

        host: the tracker ip 
        port: the tracker port number
    '''
    # client sends the name of the file that it wants to share and its connection info to the tracker node 
    listening_addr = host
    listening_port = port

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try: 
        client.connect((TRACKER_ADDR,TRACKER_PORT))
    except ConnectionRefusedError: 
        raise Exception("Tracker has not been started yet")

    with open(filename, 'rb') as f:
        while True:
            data = f.read(MAX_FILE_SIZE)
            if not data:
                break
            client.sendall(f'SEND|{filename}|{listening_addr}|{listening_port}'.encode('utf-8'))  # we have a space here so we can split it in the tracker  


    # sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.close()
    p2p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p2p.bind((listening_addr, listening_port)) # client opens a socket and waits for requests

    p2p.listen(5)
    print(f"Client running on {listening_addr}:{listening_port}")
    while True:
        conn, addr = p2p.accept()
        print(f"Connection from {addr}")
        print("Client(listening) received info: ", conn)
        threading.Thread(target=handle_client, args=(conn,username,)).start()




def request_file_from_tracker(filename=''):
    '''
        - Client requests a file using the tracker. 
        - Tracker replies with the connection information of the client which holds the file.

        host: the tracker ip 
        port: the tracker port number
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((TRACKER_ADDR,TRACKER_PORT))
    except: 
        raise Exception("Tracker has not been started yet")

    sock.sendall(f'REQUEST|{filename}'.encode('utf-8'))

    response = sock.recv(MAX_FILE_SIZE).decode('utf-8').split("|")
    # print(response)
    if response[0] == "EXISTS":
        p2p_server_addr = response[1] 
        p2p_server_port = response[2] 
        print(f"REQUESTER: FILE EXISTS - {p2p_server_addr} {p2p_server_port}")

        sock.close()
        p2p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        p2p.connect((p2p_server_addr, int(p2p_server_port)))
        p2p.send(filename.encode('utf-8'))

        response = p2p.recv(MAX_FILE_SIZE).decode('utf-8')
        if response:
            full_path = f"{os.getcwd()}/{randint(0, 100000)}{filename}"
            # print("Data: ", response) 

            filesize = int(response)
            print(f"File exists, size: {filesize} bytes")
            with open(full_path,'wb') as f:
                bytes_recieved = 0
                while bytes_recieved < filesize:
                    bytes_read = p2p.recv(1024)
                    if not bytes_read:
                        break
                    f.write(bytes_read)
                    bytes_recieved += len(bytes_read)
            print(f"Downloaded: {filename}")

        else:
            print("File does not exist.")
        
        p2p.close()
    else:
        print("Filename does not exist in tracker db.")
    
    sock.close()

def check_online_clients(host='0.0.0.0',port=12345): 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host,port))
    except: 
        raise Exception("Tracker has not been started yet")

    sock.sendall('CLIENTS|ALL'.encode('utf-8'))

    response = sock.recv(MAX_FILE_SIZE).decode('utf-8').split("|")
    print("ONLINE CLIENTS FROM TRACKER (IP:PORT)")
    for client in response: 
        print(client)


if __name__=="__main__":
    generate_auth_file()
    choice = input("start tracker (t)\nsend(s)\nfile request (f)\ncheck online clients(c)\nregister (r)?\n")
    if choice.lower() == 't':
        start_tracker()
    elif choice.lower() == 's': 
        username = login()
        listening_addr = input("Enter an address to listen on: ")
        listening_port = int(input("Enter a port to listen on: "))
        filename = input("Enter the filename to send to the tracker (max size 8kb): ")
        client_send_to_tracker(host=listening_addr, port=listening_port, filename=filename, username=username)
    elif choice.lower() == 'f':
        username = login()
        filename = input("Enter the filename to request from the tracker: ")
        request_file_from_tracker(filename=filename)
    elif choice.lower() == 'c':
        check_online_clients()
    elif choice.lower() == 'r': 
        register()


        
