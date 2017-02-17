# -*- coding: utf-8 -*-
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

client = ModbusClient(method="rtu", port="/dev/ttyUSB1",baudrate=9600,timeout=2)
client.connect()

rr = client.read_holding_registers(0x0062,4, unit=0x03)
print [hex(i) for i in rr.registers]
d = rr.registers

client.close()


from struct import pack, unpack

data_list = unpack('<6BH', pack('>4H',*d))


from pymodbus.client.sync import ModbusTcpClient
from collections import namedtuple
A = namedtuple('A', 'ip port id start_address')
client_settings = A(ip='192.168.55.4',
                    port=8000,
                    id=0x01,
                    start_address=400)

# tcp client
TCPclient = ModbusTcpClient(host=client_settings.ip, port=client_settings.port)

rq = TCPclient.write_registers(client_settings.start_address, data_list, unit=client_settings.id)
#assert(rq.function_code < 0x80)

TCPclient.close()