import socket

server_ip = ("127.0.0.1", 20001)
Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

while(True):
    message = input("Podaj wiadomosc")
    message = str.encode(message)
    Socket.sendto(message, server_ip)





