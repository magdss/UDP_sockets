import socket
import bitarray

class Client:
    server_ip = ("127.0.0.1", 20001)
    Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    session_id = 0

    OK = bitarray.bitarray([False, False, False, True])
    RETRY = bitarray.bitarray([False, False, True, True])

    GET_ID = bitarray.bitarray([False, False, False, False, True])
    SEND_L = bitarray.bitarray([False, False, False, True, False])
    SEND_GUESS = bitarray.bitarray([False, False, False, True, True])
    LOW_RANGE = bitarray.bitarray([False, False, True, False, False])
    HIGH_RANGE = bitarray.bitarray([False, False, True, True, False])
    WAIT = bitarray.bitarray([True, False, False, False, False])
    WAIT_FOR_START = bitarray.bitarray([True, True, False, False, False])
    AGAIN = bitarray.bitarray([True, True, False, True, True])

    low_range = 0
    high_range = 0



    def bit_to_int(self,b):
        i = 0
        for bit in b:
            i = (i << 1) | bit
        return i


    def count_bits(self,arr):
        b = 0
        for i in arr:
            if(i == True or i=='1'):
                b += 1
        return b


    def bitfield(self, l, n):  # zamiana liczby na bity
        return "{0:b}".format(l).zfill(n)


    def ask_for_id(self):               # funkcja wysyłająca prośbę o ID
        operation = self.GET_ID
        response = bitarray.bitarray(4)
        response.setall(False)
        id = bitarray.bitarray(6)
        id.setall(False)
        data = bitarray.bitarray(10)
        data.setall(False)
        fill = bitarray.bitarray(4)
        fill.setall(False)
        cont = self.count_bits(operation) + self.count_bits(response) + self.count_bits(id) + self.count_bits(data)
        control_sum = self.bitfield(cont ,11)

        header = [operation, response, id, data, control_sum, fill]

        message = bitarray.bitarray(endian='big')
        for i in range(6):
            message += header[i]
        message = message.tobytes()

        self.Socket.sendto(message, self.server_ip)
        print("Wysłana prośba o uzyskanie ID")
        received = self.Socket.recvfrom(5)
        received_msg = bitarray.bitarray()
        received_msg.frombytes(received[0])
        my_id = received_msg[9:15]
        my_id = self.bit_to_int(my_id)
        self.session_id = my_id
        print(self.session_id)
        print("ID uzyskane od serwera: ", my_id)


    def send_L(self):               #wysyłanie liczby L
        l = int(input("Podaj liczbe z przedziału 1-512: "))
        operation = self.SEND_L
        response = bitarray.bitarray(4)
        response.setall(False)
        id = self.bitfield(self.session_id,6)
        data = self.bitfield(l,10)
        contr = self.count_bits(operation) + self.count_bits(response) + self.count_bits(id) + self.count_bits(data)
        control_sum = self.bitfield(contr,11)
        fill = bitarray.bitarray()
        fill.setall(False)

        header = [operation, response, id, data, control_sum, fill]
        print(header)
        message = bitarray.bitarray(endian='big')

        for i in header:
            message += i

        message = message.tobytes()

        self.Socket.sendto(message, self.server_ip)

        answer = self.Socket.recvfrom(5)
        received_msg = bitarray.bitarray()
        received_msg.frombytes(answer[0])

        if(received_msg[5:9] == self.OK):
            print("Serwer zaakceptował twoją liczbę")
        else:
            print("Serwer już przyjął taką liczbę. Podaj inną liczbę.")
            self.send_L()

    def wait(self):
        while(True):
            received = self.Socket.recvfrom(5)
            received_msg = bitarray.bitarray()
            received_msg.frombytes(received[0])
            if(received_msg[:5] == self.WAIT):
                print("Oczekiwanie na podanie liczb przez innych graczy")
            if(received_msg[:5] == self.WAIT_FOR_START):
                print("Wszyscy gracze się połączyli. Oczekiwanie na start gry.")
            if(received_msg[:5] == self.AGAIN):
                print("Liczby podane przez graczy nie spełniają wymagań. Proszę podać kolejne liczby")
                self.send_L()

            if(received_msg[:5] == self.LOW_RANGE):
                d = received_msg[15:25]
                d = self.bit_to_int(d)
                self.low_range = d
                print("Wylosowana liczba jest większa niż " , self.low_range)

            if(received_msg[:5] == self.HIGH_RANGE_RANGE):
                d = received_msg[15:25]
                d = self.bit_to_int(d)
                self.high_range = d
                print("Wylosowana liczba jest mniejsza niż ", self.high_range)




if __name__ == "__main__" :
    c = Client()
    c.ask_for_id()
    c.send_L()
    c.wait()


