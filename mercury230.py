# -*- coding: utf-8 -*-
import serial
import crc16
from struct import pack, unpack

#for debug
#import sys
#sys.path.append("d:\Azat\PycharmProjects\mbgate\mercury\")

def convert(int_value):
   encoded = format(int_value, 'x')
   length = len(encoded)
   encoded = encoded.zfill(length+length%2)
   return encoded.decode('hex')

def oneRXTX(intAddress, strCmd):
    rq = convert(intAddress)+strCmd
    rq = rq + convert(crc16.calcString(rq, crc16.INITIAL_MODBUS))[::-1]
    ser.write(rq)
    rs = ser.read(size=100)
    if convert(crc16.calcString(rs[:-2], crc16.INITIAL_MODBUS)) == rs[-2:][::-1]:
        crcCheck = "CRC OK"
        crcCheckOK = True
    else:
        crcCheck = "CRC BAD!!!"
        crcCheckOK = False
    print "request:\t", hexString(rq), "\nresponse:\t", hexString(rs), '\n', crcCheck
    return crcCheckOK, rs

#if __name__ == '__main__':

hexString = lambda byteString : " ".join(x.encode('hex') for x in byteString)

ser = serial.Serial(
    port='COM5',
    baudrate=9600,
    bytesize=8,
    parity='N',
    stopbits=1,
    timeout=0.5,
    xonxoff=0,
    rtscts=0
)

#sample rq&rs
getPowerCRC = "\xB0\x00\x74\x70"
ser.write(getPowerCRC)
response = ser.read(size=100)
print "write: {}\nread:  {}".format(hexString(getPowerCRC),hexString(response))

address = 176
cmdList = [
    "\x00", #echo
    "\x01\x01\x01\x01\x01\x01\x01\x01", #set connection via password
    "\x08\x00", # SN and date
    "\x08\x02", # коэф трансформации
    "\x08\x12", # вариант исполнения
    # накопленные
    "\x05\x00\x00", #сумма по Тарифам
    "\x05\x00\x01", #Т1
    "\x05\x00\x02", #Т2
    "\x05\x60\x00", #сумма по Тарифам (по фазно)
    "\x05\x60\x01", #Т1(по фазно)
    "\x05\x60\x02", #Т1(по фазно)
]
#Instant values
cmdInst = [
    "\x08\x11\x11", # Ua/100
    "\x08\x11\x12", # Ub/100
    "\x08\x11\x12", # Uc/100
    "\x08\x11\x21", # Ia/1000
    "\x08\x11\x22", # Ib/1000
    "\x08\x11\x22", # Ic/1000
    "\x08\x11\x40", # Hz/100
    "\x08\x11\x00", # Psum/100
    "\x08\x11\x01", # Pa/100
    "\x08\x11\x02", # Pb/100
    "\x08\x11\x03", # Pc/100
]
for cmd in cmdList:
    oneRXTX(address,cmd)

def bytesToINT32(bytes):
    if len(bytes)==4:
        int32 = "".join(x.encode('hex') for x in [bytes[1], bytes[0], bytes[3],bytes[2]])
        int32 = int(int32, 16)
        print int32
        return int32
    else:
        return 0

def int32struct(bytes):
    l1 = len(bytes)
    if l1%4 == 0:
        l4 = l1/4
        print unpack(">{}I".format(l4),
                     pack('<{}h'.format(l4*2), *unpack('>{}h'.format(l4*2), bytes)))


def int16struct(bytes):
    if len(bytes)==2:
        print unpack('<H', bytes)

for cmd in cmdList[5:]:
    checkOK, rs = oneRXTX(address,cmd)
    if checkOK:
        #bytesToINT32(rs[1:5])
        #bytesToINT32(rs[9:13])
        int32struct(rs[1:][:-2])

for cmd in cmdInst:
    checkOK, rs = oneRXTX(address,cmd)
    if checkOK:
        int16struct(rs[2:][:-2])

ser.close()