import socket

local_ip = "127.0.0.1"
port = 20001

Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
Socket.bind((local_ip, port))

while(True):
    received_bytes = Socket.recvfrom(1024)
    message = received_bytes[0]
    print(message.decode())