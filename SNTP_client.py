
import datetime
import struct
import time
from socket import *

client = socket(SOCK_DGRAM)
data = ('\x1b' + 47 * '\0').encode('utf-8')
ip = input()
client.connect((ip, 123))
client.send(data)
data, address = client.recvfrom(1024)
if data:
    t = struct.unpack('!12I', data)[10]
    print('Time_from_server=%s' % time.ctime(t))
    print('Time_now=%s' % datetime.datetime.now())
