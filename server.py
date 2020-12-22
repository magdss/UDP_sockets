import socket
import bitarray
import random

# wzory operacji

GET_ID = bitarray.bitarray([False,False,False,False,True])


def bitfield(n):  # zamiana liczby na bity
    return [int(digit) for digit in bin(n)[2:]]


clients_id = []             # lista id klientów

local_ip = "127.0.0.1"
port = 20001

Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
Socket.bind((local_ip, port))

while(True):
    received_bytes = Socket.recvfrom(5) # odebranie wiadomości
    address = received_bytes[1]     # pobranie adresu nadawcy informacji
    message = received_bytes[0]
    message_bit = bitarray.bitarray()
    message_bit.frombytes(message)     # zamiana wiadomości na bity

    # podział wiadomości na pola:
    operation = message_bit[:5]
    response = message_bit[5:9]
    id = message_bit[9:15]
    data = message_bit[15:25]
    control_sum = message_bit[25:36]
    fill = message_bit[36:]

    print("Received message from:", id, "is", message_bit)

    if(operation == GET_ID):     # sprawdzenie czy klient prosi o przydzielenie ID
        while(True):             # losowanie unikalnego ID (nieprzypisanego  do innego klienta)
            new_id = random.randint(1,32)
            if(new_id not in clients_id ):
                break
        clients_id.append(new_id)     # dodanie nowego ID do listy klientów

        print(new_id)
        new_id = "{0:b}".format(new_id).zfill(6)
        id_to_send = bitarray.bitarray()
        id_to_send += new_id   # zamiana id na bity
        print(id_to_send)



