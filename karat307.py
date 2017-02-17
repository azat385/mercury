# -*- coding: utf-8 -*-

import sys

from collections import namedtuple
A = namedtuple('A', 'ip port id start_address')

if len(sys.argv) >= 2:
    address = int(sys.argv[1])
    start_address = int(sys.argv[2])
else:
    address = 0x03
    start_address = 400

client_settings = A(ip='192.168.55.4',
                    port=8000,
                    id=0x01,
                    start_address=start_address)

# rtu master
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
client = ModbusClient(method="rtu", port="/dev/ttyUSB1",baudrate=9600,timeout=2)
client.connect()

rr = client.read_holding_registers(0x0062,4, unit=address)
print [hex(i) for i in rr.registers]
d = rr.registers
client.close()

# transform the data
from struct import pack, unpack
data_list = unpack('<6BH', pack('>4H',*d))

# tcp client
from pymodbus.client.sync import ModbusTcpClient
TCPclient = ModbusTcpClient(host=client_settings.ip, port=client_settings.port)

rq = TCPclient.write_registers(client_settings.start_address, data_list, unit=client_settings.id)
#assert(rq.function_code < 0x80)

TCPclient.close()