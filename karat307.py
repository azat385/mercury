# -*- coding: utf-8 -*-

import sys

from collections import namedtuple
A = namedtuple('A', 'ip port id start_address')

if len(sys.argv) >= 2:
    address = int(sys.argv[1])
    start_address = int(sys.argv[2])
else:
    address = 0x03
    start_address = 500

client_settings = A(ip='192.168.55.4',
                    port=8000,
                    id=0x01,
                    start_address=start_address)

# rtu master
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
client = ModbusClient(method="rtu", port="/dev/ttyUSB1",baudrate=9600,timeout=2)
client.connect()

rr = client.read_holding_registers(0x0062, 4, unit=address)
print [hex(i) for i in rr.registers]
d = rr.registers

regs_rr = [
    [0x1100,  4],   # f1, f2
    [0x1120,  6],   # t1, t2, delta_t
    [0x1140,  4],   # p1, p2
    [0x1160,  4],   # m1, m2
    [0x1180,  2],   # q1
    [0x130e, 16],   # e1, m1, m2, delta_m, t1, t2, p1, p2
    [0x132c,  2],   # v3
]
regs = []
for data in regs_rr:
    rr = client.read_holding_registers(*data, unit=address)
    regs += rr.registers

client.close()

# transform the data
from struct import pack, unpack
# sec, min, hour, day, week, month, year
data_list = list (unpack('<6BH', pack('>4H',*d)))   # unpack returns tuple
data_list += regs

# tcp client
from pymodbus.client.sync import ModbusTcpClient
TCPclient = ModbusTcpClient(host=client_settings.ip, port=client_settings.port)

rq = TCPclient.write_registers(client_settings.start_address, data_list, unit=client_settings.id)
#assert(rq.function_code < 0x80)

TCPclient.close()
exit()

#================================for debug==========================
rr = client.read_holding_registers(0x0106,5, unit=3)
len(rr.registers)#28
bytes_array = unpack('<56B', pack('>28H',*rr.registers))
for i in range(len(bytes_array)):
    print i, hex(bytes_array[i])

from struct import pack, unpack
def print_32bit_float(reg1, reg2):
    return unpack('>f', pack('>2H',reg2, reg1))[0]

def print_32bit_int(reg1, reg2):
    return unpack('>L', pack('>2H',reg1, reg2))[0]

rr = client.read_holding_registers(0x2000,110, unit=3)
for i in range(0, len(rr.registers), 2):
    print i / 2, print_32bit_float(*(rr.registers[i:i + 2])), print_32bit_int(*(rr.registers[i:i + 2]))


def singleRead(start, quantity):
    rr = client.read_holding_registers(start, quantity, unit=address)
    for i in range(0, len(rr.registers), 2):
        print i / 2, print_32bit_float(*(rr.registers[i:i + 2])), print_32bit_int(*(rr.registers[i:i + 2]))

singleRead(0x1100,4)

desc106 = {
    0x1 : "Volume",
    0x2 : "Massa",
    0x3 : "Temper",
    0x4 : "Press",
    0x5 : "Energy",
    0x6 : "Electro1",
    0x7 : "Electro2",
    0x8 : "Electro3",
    0x9 : "Electro4",
    0xA : "Date_Time",
    0xB : "Narabotka",
    0xC : "Errors",
    0xF : "End",
    0xD1 : "Tmin",
    0xD2 : "Tmax",
    0xD3 : "Tdt",
    0xD4 : "Tf",
    0xD5 : "Tep",
    0xD6 : "Tns",
}


def read106():
    r = client.read_holding_registers(0x0106, 5, unit=address)
    #len(rr.registers)  = 28 in any case
    bytes_array = unpack('<56B', pack('>28H', *r.registers))
    return_str = []
    for i in range(len(bytes_array)):
        byte_part1 = (bytes_array[i] & 0xF0) >> 4
        byte_part2 = (bytes_array[i] & 0x0F)
        byte_whole = bytes_array[i]
        if byte_whole in desc106:
            desc106_str = desc106[byte_whole]
        else:
            if byte_part1 in desc106:
                desc106_str = "{} channel {}".format(desc106[byte_part1],byte_part2+1)
            else:
                desc106_str = "UNKNOWN"
        return_str.append("No{} {}".format(i, desc106_str))
    return return_str

def singleReadDesc106(start, quantity):
    rr = client.read_holding_registers(start, quantity, unit=address)
    r106 = read106()
    for i in range(0, len(rr.registers), 2):
        print r106[i/2+1],  'hex:',hex(start+i),\
            print_32bit_float(*(rr.registers[i:i + 2]))#, print_32bit_int(*(rr.registers[i:i + 2]))


singleReadDesc106(0x1300,110)
# e1, m1, m2, delta_m, t1, t2, p1, p2
'''
No8 Energy channel 1    hex: 0x130e     1368.40600586
No9 Massa channel 1     hex: 0x1310     90862.015625
No10 Massa channel 2    hex: 0x1312     91013.3203125
No11 Massa channel 3    hex: 0x1314     -151.313278198
No12 Temper channel 1   hex: 0x1316     70.9523925781
No13 Temper channel 2   hex: 0x1318     51.4228820801
No14 Press channel 1    hex: 0x131a     4.59449386597
No15 Press channel 2    hex: 0x131c     3.75863051414
No23 Volume channel 3   hex: 0x132c     3.59999918938
'''
