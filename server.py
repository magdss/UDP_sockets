import socket
import bitarray
import random
import threading
import sys

# wzory operacji

GET_ID = bitarray.bitarray([False, False, False, False, True])     #prośba o id
SEND_L = bitarray.bitarray([False, False, False, True, False])      #wysłanie liczby do zakresu
SEND_GUESS = bitarray.bitarray([False, False, False, True, True])   #wysłanie zgadywanej liczby
LOW_RANGE = bitarray.bitarray([False, False, True, False, False])   #wysłanie dolnego zakresu liczb
HIGH_RANGE = bitarray.bitarray([False, False, True, True, False])   #wysłanie górnego zakresu liczb
WAIT = bitarray.bitarray([True, False, False, False, False])        #prośba o czekanie na polaczenie reszty
WAIT_FOR_START = bitarray.bitarray([True, True, False, False, False])   #czekaj 30 sek na start
AGAIN = bitarray.bitarray([True, True, False, True, True])          #podane liczby nie spelniaja zalozen, podaj ponownie
START = bitarray.bitarray([True, True, True, False, False])         #start gry
END = bitarray.bitarray([True, True, True, True, True])             #koniec gry i podanie liczby prob
WINNER = bitarray.bitarray([False, False, True, True, True])        #podanie zwyciezcy


#wzory odpowiedzi

OK = bitarray.bitarray([False, False, False, True])
RETRY = bitarray.bitarray([False, False, True, True])
NOT_WIN = bitarray.bitarray([False, False, True, False])
WIN = bitarray.bitarray([True, True, True, True])


def bitfield(l, n):  # zamiana liczby na bity       l-liczba, n-na ilu bitach ma byc zapisana
    return "{0:b}".format(l).zfill(n)


def bit_to_int(b):      #zamiana pitow na liczby
    i = 0
    for bit in b:
        i = (i << 1) | bit
    return i


def count_bits(arr):        #liczy 1 w ciagu bitow
    b = 0
    for i in arr:
        if(i == True):
            b += 1
    return b


def start_game(ids, adr):               #funkcja startujaca gre
    for x,y in zip(ids,adr):
        id = bitfield(x, 6)
        dt = bitfield(0,10)
        contr = count_bits(START) + count_bits(OK) + count_bits(id) + count_bits(dt)
        control_sum = bitfield(contr, 11)
        header = [START, OK, id, dt, control_sum, fill]
        message_to_send = bitarray.bitarray(endian='big')
        for i in range(5):
            message_to_send += header[i]

        message_to_send = message_to_send.tobytes()
        Socket.sendto(message_to_send, y)






clients_id = []             # lista id klientów
adresses = []               #lista adresow
id_try = {}                 #slownik id-liczba prob
L = []                      #podane liczby do zakresu
value = 0                   #wylosowana przez serwer watosc
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
        id_try[new_id] = 0
        print("Podłączono nowego klienta. ID nowego klienta to: ", new_id)

        new_id = bitfield(new_id,6)
        id_to_send = bitarray.bitarray()
        id_to_send += new_id   # zamiana id na bity
        contr = count_bits(operation) + count_bits(OK) + count_bits(id_to_send) + count_bits(data)      #policzenie sumy kontrolne
        control_sum = bitfield(contr,11)
        header = [operation, OK, id_to_send, data, control_sum, fill]
        message_to_send = bitarray.bitarray(endian='big')
        for i in range(5):              #złożenie wiadomości
            message_to_send += header[i]

        message_to_send = message_to_send.tobytes()
        Socket.sendto(message_to_send, address)         #wysłanie wiadomości

    if(operation == SEND_L):                #jeśli klient przesyła liczbe do stworzenia zakresu
        l = bit_to_int(data)                #zamiana bitów na liczbe
        if(l not in L):                 #jezeli nikt nie podal takiej liczby
            L.append(l)                 #dodanie liczby do listy
            contr = count_bits(operation) + count_bits(OK) + count_bits(id) + count_bits(data)
            control_sum = bitfield(contr, 11)
            header = [SEND_L, OK, id, data, control_sum, fill]
            message_to_send = bitarray.bitarray(endian='big')
            for i in range(5):
                message_to_send += header[i]

            message_to_send = message_to_send.tobytes()
            Socket.sendto(message_to_send, address)
            if(len(L)<3):               # jeżeli jest mniej niż 3 liczby
                dt = bitarray.bitarray(10)
                dt.setall(False)
                contr = count_bits(WAIT) + count_bits(OK) + count_bits(id) + count_bits(dt)
                control_sum = bitfield(contr,11)
                header = [WAIT, OK, id, dt, control_sum, fill]      #złożenie komunikatu z prosba o czekanie
                message_to_send = bitarray.bitarray(endian='big')
                for i in range(5):
                    message_to_send += header[i]

                message_to_send = message_to_send.tobytes()
                Socket.sendto(message_to_send, address)
            if(len(L)>=3):          # jezeli są 3 lub wiecej cyfry
                L.sort(reverse=True)    #sortowanie
                L1 = L[0]-L[2]              #obliczenia na liczbach
                L2 = L[1]+L[2]
                buf = L1
                if(L1>L2):
                    L1 = L2
                    L2 = buf
                if(abs(L1-L2)<10):              #jeżeli zakres jest mniejszy niż 10
                    dt = bitarray.bitarray(10)
                    dt.setall(False)
                    L = []                  #wyzerowanie liczb
                    for u,a in zip(clients_id, adresses):       #przejście po wszystkich klientach
                        id = bitfield(u,6)
                        contr = count_bits(AGAIN) + count_bits(OK) + count_bits(id) + count_bits(dt)    #prośba o ponowne wysłanie liczb
                        control_sum = bitfield(contr,11)
                        header = [AGAIN, OK, id, dt, control_sum, fill]
                        message_to_send = bitarray.bitarray(endian='big')
                        for i in range(5):
                            message_to_send += header[i]

                        message_to_send = message_to_send.tobytes()
                        Socket.sendto(message_to_send, a)
                else:               #jeżeli zakres wiekszy niz 10
                    value = random.randint(L1, L2)          #wylosowanie wartosci przez serwer
                    print("Wartość: ", value)
                    dt = bitfield(L1,10)                            #dolny i gorny zakres wysyłany jest w polu data
                    for u,a in zip(clients_id, adresses):           #przejście po wszystkich klientach
                        id = bitfield(u,6)
                        contr = count_bits(LOW_RANGE) + count_bits(OK) + count_bits(id) + count_bits(dt)        #informacja o dolnym zakresie
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
                        contr = count_bits(HIGH_RANGE) + count_bits(OK) + count_bits(id) + count_bits(dt)       #informacja o gornym zakresie
                        control_sum = bitfield(contr,11)
                        header = [HIGH_RANGE, OK, id, dt, control_sum, fill]
                        message_to_send = bitarray.bitarray(endian='big')
                        for i in range(5):
                            message_to_send += header[i]

                        message_to_send = message_to_send.tobytes()
                        Socket.sendto(message_to_send, a)

                    dt = bitfield(0,10)
                    for u,a in zip(clients_id, adresses):           #po wysłaniu zakresów przejście po adresach i wysłanie prośby o poczekanie 30 sek
                        id = bitfield(u,6)
                        contr = count_bits(WAIT_FOR_START) + count_bits(OK) + count_bits(id) + count_bits(dt)
                        control_sum = bitfield(contr,11)
                        header = [WAIT_FOR_START, OK, id, dt, control_sum, fill]
                        message_to_send = bitarray.bitarray(endian='big')
                        for i in range(5):
                            message_to_send += header[i]

                        message_to_send = message_to_send.tobytes()
                        Socket.sendto(message_to_send, a)
                    T = threading.Timer(30.0, start_game, [clients_id, adresses])       #stworzenie nowego wątku, z opoznieniem 30 sek (opoznienie, wywoływana funkcja, [argumenty])
                    T.start()





        else:                #jeżeli liczba została już podana to prosba o ponowne wysłanie do klienta
            contr = count_bits(SEND_L) + count_bits(RETRY) + count_bits(id) + count_bits(data)
            control_sum = bitfield(contr, 11)
            header = [SEND_L, RETRY, id, data, control_sum, fill]
            message_to_send = bitarray.bitarray(endian='big')
            for i in range(5):
                message_to_send += header[i]

            message_to_send = message_to_send.tobytes()
            Socket.sendto(message_to_send, address)


    if(operation == SEND_GUESS):            #jeżeli gracz wysyła zgadywaną liczbę
        guessed_number = bit_to_int(data)   #zamiana bitow na liczbe

        if(guessed_number == value):        #jeżeli gracz zgadł wysłanie wiadomosci o wygranej
            contr = count_bits(SEND_GUESS) + count_bits(WIN) + count_bits(id) + count_bits(data)
            control_sum = bitfield(contr, 11)
            header = [SEND_GUESS, WIN, id, data, control_sum, fill]
            message_to_send = bitarray.bitarray(endian='big')
            for i in range(5):
                message_to_send += header[i]
            id = bit_to_int(id)
            id_try[id] += 1             #zwiększenie liczby prób danego gracza

            message_to_send = message_to_send.tobytes()
            Socket.sendto(message_to_send, address)
            for x, y in zip(clients_id, adresses):          #wysłanie do wszystkich graczy wiadomości o koncu gry
                id_d = bitfield(x, 6)
                number_of_tries = id_try[id]
                dt = bitfield(number_of_tries, 10)
                print(dt)
                contr = count_bits(END) + count_bits(OK) + count_bits(id_d) + count_bits(dt)            #wiadomosc o koncu gry i ilosci prob
                control_sum = bitfield(contr, 11)
                header = [END, OK, id_d, dt, control_sum, fill]
                message_to_send = bitarray.bitarray(endian='big')
                for i in range(5):
                    message_to_send += header[i]

                message_to_send = message_to_send.tobytes()
                Socket.sendto(message_to_send, y)
            for x, y in zip(clients_id, adresses):
                id_d = bitfield(x, 6)
                dt = bitfield(id, 10)

                contr = count_bits(WINNER) + count_bits(OK) + count_bits(id_d) + count_bits(dt)         #wiadomosc o id zwyciezcy
                control_sum = bitfield(contr, 11)
                header = [WINNER, OK, id_d, dt, control_sum, fill]
                message_to_send = bitarray.bitarray(endian='big')
                for i in range(5):
                    message_to_send += header[i]

                message_to_send = message_to_send.tobytes()
                Socket.sendto(message_to_send, y)




        else:           #jeżeli gracz nie zgadł liczby wysłanie odpowiedniej odpowiedzi


            contr = count_bits(SEND_GUESS) + count_bits(NOT_WIN) + count_bits(id) + count_bits(data)
            control_sum = bitfield(contr, 11)
            header = [SEND_GUESS, NOT_WIN, id, data, control_sum, fill]
            message_to_send = bitarray.bitarray(endian='big')
            for i in range(5):
                message_to_send += header[i]

            id = bit_to_int(id)
            id_try[id] += 1         #zwiększenie liczby prób
            message_to_send = message_to_send.tobytes()
            Socket.sendto(message_to_send, address)






