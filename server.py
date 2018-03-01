import datetime
import math
import socket
import time
import parser_config
import hashlib

class Server:

    def __init__(self, server_address, seconds_of_lies):
        self.seconds_of_lies = seconds_of_lies
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = server_address
        self.sock.bind((self.server_address, 123))
        self.connections = {}

        self.LI = 128
        self.Mode = 4
        self.precision = abs(int(math.log(time.clock(), 2)))
        self.reference_ID = b'LOCL'
        self.starting_point = datetime.datetime(1900, 1, 1, tzinfo=datetime.timezone.utc)
        self.start_server_time = datetime.datetime.now(tz=datetime.timezone.utc)
        self.reference_timestamp = self.get_time_per_second_from_start_point(self.start_server_time)

    def start_server(self):
        print('Server was started')
        while True:
            try:
                data, addr = self.sock.recvfrom(48)
                if len(data) < 48:
                    continue
                self.send_time(addr, data, datetime.datetime.now(tz=datetime.timezone.utc))
            except socket.error:
                continue

    def get_sntp_frame(self, data_from_request, receive_time):
        sntp_frame = bytearray()
        vn = self.get_vn_from_client(data_from_request[0])
        sntp_frame.append(self.LI + vn + self.Mode)
        sntp_frame.append(0)
        sntp_frame.append(data_from_request[2])
        sntp_frame.append(self.precision)
        for i in range(0, 8):
            sntp_frame.append(0)
        sntp_frame += self.reference_ID
        sntp_frame += self.reference_timestamp[0] + self.reference_timestamp[1]
        originate_timestamp = bytearray()
        for i in range(0, 8):
            originate_timestamp.append(data_from_request[40 + i])
        sntp_frame += originate_timestamp
        receive_time_per_byte = self.get_time_per_second_from_start_point(receive_time)
        sntp_frame += receive_time_per_byte[0] + receive_time_per_byte[1]
        transmit_time = self.get_time_per_second_from_start_point(datetime.datetime.now(tz=datetime.timezone.utc),
                                                                  self.seconds_of_lies)
        sntp_frame += transmit_time[0] + transmit_time[1]
        #hash_frame = hashlib.md5()
        #hash_frame.update(sntp_frame)
        #sntp_frame += str(hash_frame.hexdigest()).encode('utf-8')
        #sntp_frame += hash_frame.digest()
        #print(len(sntp_frame))
        return sntp_frame

    def get_vn_from_client(self, first_byte_from_client_title_frame):
        return (int(first_byte_from_client_title_frame) & 0b00111000)

    def get_time_per_second_from_start_point(self, date, false_seconds=0):
        difference = (date - self.starting_point).total_seconds()
        second_to_byte = int(difference + false_seconds).to_bytes(4, 'big')
        milliseconds_to_byte = (int(str(difference).split('.')[1])).to_bytes(4, 'big')
        return second_to_byte, milliseconds_to_byte

    def send_time(self, addr, data, receive_time):
        sntp_frame = self.get_sntp_frame(data, receive_time)
        self.sock.sendto(sntp_frame, addr)


if __name__ == '__main__':
    pars = parser_config.ParserConfig('config_server.conf')
    try:
        pars.parse()
    except parser_config.ParserException as exc:
        print("Exception in config file, server will be start with default config")
    serv = Server(pars.ip_address, pars.wrong_time)
    serv.start_server()
