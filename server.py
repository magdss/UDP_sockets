import socket
import bitarray
import random

# wzory operacji

GET_ID = bitarray.bitarray([False, False, False, False, True])
SEND_L = bitarray.bitarray([False, False, False, True, False])
SEND_GUESS = bitarray.bitarray([False, False, False, True, True])
LOW_RANGE = bitarray.bitarray([False, False, True, False, False])
HIGH_RANGE = bitarray.bitarray([False, False, True, True, False])
WAIT = bitarray.bitarray([True, False, False, False, False])
WAIT_FOR_START = bitarray.bitarray([True, True, False, False, False])
AGAIN = bitarray.bitarray([True, True, False, True, True])
START = bitarray.bitarray([True, True, True, False, False])


#wzory odpowiedzi

OK = bitarray.bitarray([False, False, False, True])
RETRY = bitarray.bitarray([False, False, True, True])
NOT_WIN = bitarray.bitarray([False, False, True, False])
WIN = bitarray.bitarray([True, True, True, True])


def bitfield(l, n):  # zamiana liczby na bity
    return "{0:b}".format(l).zfill(n)


def bit_to_int(b):
    i = 0
    for bit in b:
        i = (i << 1) | bit
    return i


def count_bits(arr):
    b = 0
    for i in arr:
        if(i == True):
            b += 1
    return b





clients_id = []             # lista id klientów
adresses = []
L = []
value = 0
local_ip = "127.0.0.1"
port = 20001
print("Startowanie serwera .........")
Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
Socket.bind((local_ip, port))

while(True):
    received_bytes = Socket.recvfrom(5) # odebranie wiadomości
    address = received_bytes[1]     # pobranie adresu nadawcy informacji
    if(address not in adresses):
        adresses.append(address)
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

    print("Otrzymana wiadomosc od klienta o ID:", bit_to_int(id), "to ", message_bit)

    if(operation == GET_ID):     # sprawdzenie czy klient prosi o przydzielenie ID
        while(True):             # losowanie unikalnego ID (nieprzypisanego  do innego klienta)
            new_id = random.randint(1,32)
            if(new_id not in clients_id ):
                break
        clients_id.append(new_id)     # dodanie nowego ID do listy klientów
        print("Podłączono nowego klienta. ID nowego klienta to: ", new_id)

        new_id = bitfield(new_id,6)
        id_to_send = bitarray.bitarray()
        id_to_send += new_id   # zamiana id na bity
        contr = count_bits(operation) + count_bits(OK) + count_bits(id_to_send) + count_bits(data)
        control_sum = bitfield(contr,11)
        header = [operation, OK, id_to_send, data, control_sum, fill]
        message_to_send = bitarray.bitarray(endian='big')
        for i in range(5):
            message_to_send += header[i]

        message_to_send = message_to_send.tobytes()
        Socket.sendto(message_to_send, address)

    if(operation == SEND_L):
        l = bit_to_int(data)
        if(l not in L):
            L.append(l)
            contr = count_bits(operation) + count_bits(OK) + count_bits(id) + count_bits(data)
            control_sum = bitfield(contr, 11)
            header = [SEND_L, OK, id, data, control_sum, fill]
            message_to_send = bitarray.bitarray(endian='big')
            for i in range(5):
                message_to_send += header[i]

            message_to_send = message_to_send.tobytes()
            Socket.sendto(message_to_send, address)
            if(len(L)<3):
                dt = bitarray.bitarray(10)
                dt.setall(False)
                contr = count_bits(WAIT) + count_bits(OK) + count_bits(id) + count_bits(dt)
                control_sum = bitfield(contr,11)
                header = [WAIT, OK, id, dt, control_sum, fill]
                message_to_send = bitarray.bitarray(endian='big')
                for i in range(5):
                    message_to_send += header[i]

                message_to_send = message_to_send.tobytes()
                Socket.sendto(message_to_send, address)
            if(len(L)>=3):
                L.sort(reverse=True)
                L1 = L[0]-L[2]
                L2 = L[1]+L[2]
                if(abs(L1-L2)<10):
                    dt = bitarray.bitarray(10)
                    dt.setall(False)
                    L = []
                    for u,a in zip(clients_id, adresses):
                        id = bitfield(u,6)
                        contr = count_bits(AGAIN) + count_bits(OK) + count_bits(id) + count_bits(dt)
                        control_sum = bitfield(contr,11)
                        header = [AGAIN, OK, id, dt, control_sum, fill]
                        message_to_send = bitarray.bitarray(endian='big')
                        for i in range(5):
                            message_to_send += header[i]

                        message_to_send = message_to_send.tobytes()
                        Socket.sendto(message_to_send, a)
                else:
                    value = random.randint(L1, L2)
                    dt = bitfield(L1,10)
                    for u,a in zip(clients_id, adresses):
                        id = bitfield(u,6)
                        contr = count_bits(LOW_RANGE) + count_bits(OK) + count_bits(id) + count_bits(dt)
                        control_sum = bitfield(contr,11)
                        header = [LOW_RANGE, OK, id, dt, control_sum, fill]
                        message_to_send = bitarray.bitarray(endian='big')
                        for i in range(5):
                            message_to_send += header[i]

                        message_to_send = message_to_send.tobytes()
                        Socket.sendto(message_to_send, a)
                    dt = bitfield(L2,10)
                    for u,a in zip(clients_id, adresses):
                        id = bitfield(u,6)
                        contr = count_bits(HIGH_RANGE) + count_bits(OK) + count_bits(id) + count_bits(dt)
                        control_sum = bitfield(contr,11)
                        header = [HIGH_RANGE, OK, id, dt, control_sum, fill]
                        message_to_send = bitarray.bitarray(endian='big')
                        for i in range(5):
                            message_to_send += header[i]

                        message_to_send = message_to_send.tobytes()
                        Socket.sendto(message_to_send, a)




        else:
            contr = count_bits(operation) + count_bits(RETRY) + count_bits(id) + count_bits(data)
            control_sum = bitfield(contr, 11)
            header = [SEND_L, RETRY, id, data, control_sum, fill]
            message_to_send = bitarray.bitarray(endian='big')
            for i in range(5):
                message_to_send += header[i]

            message_to_send = message_to_send.tobytes()
            Socket.sendto(message_to_send, address)







