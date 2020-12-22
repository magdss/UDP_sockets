import socket
import bitarray



server_ip = ("127.0.0.1", 20001)
Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
id = 0

def ask_for_id():               # funkcja wysyłająca prośbę o ID
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

    header = [operation, response, id, data, control_sum, fill]

    message = bitarray.bitarray(endian='big')
    for i in range(6):
        message += header[i]

    print(message)
    message = message.tobytes()

    Socket.sendto(message, server_ip)




if __name__ == "__main__" :
    ask_for_id()