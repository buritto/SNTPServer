import datetime
import math
import socket
import time
import parser_config
import hashlib
import threading

class Server:

    def __init__(self, server_address, seconds_of_lies):
        self.seconds_of_lies = seconds_of_lies
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = server_address
        self.sock.bind((self.server_address, 123))

        self.LI = 1 << 6
        self.mode = 4
        self.stratum = 1
        self.precision = abs(int(math.log(time.perf_counter(), 2)))
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
                tr = threading.Thread(target=self.send_time, args=(addr, data, datetime.datetime.now(tz=datetime.timezone.utc)))
                tr.start()		
            except socket.error:
                continue

    def get_sntp_frame(self, data_from_request, receive_time):
        sntp_frame = bytearray()
        vn = self.get_vn_from_client(data_from_request[0])
        sntp_frame += (self.LI + vn + self.mode).to_bytes(1, 'big')
        sntp_frame += self.stratum.to_bytes(1, 'big')
        sntp_frame += data_from_request[2].to_bytes(1, 'big')
        sntp_frame += self.precision.to_bytes(1, 'big')
        for i in range(0, 8):
            sntp_frame.append(0)
        sntp_frame += self.reference_ID
        sntp_frame += self.reference_timestamp[0] + self.reference_timestamp[1]
        originate_timestamp = bytearray()
        for i in range(0, 8):
            originate_timestamp += data_from_request[40 + i].to_bytes(1, 'big')
        sntp_frame += originate_timestamp
        receive_time_per_byte = self.get_time_per_second_from_start_point(receive_time, self.seconds_of_lies)
        sntp_frame += receive_time_per_byte[0] + receive_time_per_byte[1]
        transmit_time = self.get_time_per_second_from_start_point(datetime.datetime.now(tz=datetime.timezone.utc),
                                                                  self.seconds_of_lies)
        sntp_frame += transmit_time[0] + transmit_time[1]
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
