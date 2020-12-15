import socket
import bitarray

server_ip = ("127.0.0.1", 20001)
Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


operation = bitarray.bitarray(5)
operation.setall(False)
operation[4] = True
response = bitarray.bitarray(4)
response.setall(False)
id = bitarray.bitarray(6)
id.setall(False)
data = bitarray.bitarray(10)
data.setall(False)
fill = bitarray.bitarray(4)
fill.setall(False)
control_sum = bitarray.bitarray(11)
control_sum.setall(False)

header = [operation, response, id, data, fill]

message = bitarray.bitarray(endian='big')

for i in range(5):
    message += header[i]

message = message.tobytes()

Socket.sendto(message, server_ip)



