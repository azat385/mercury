# -*- coding: utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler

# format the log entries
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

handler = RotatingFileHandler('merc2db.log',
                              mode='a',
                              maxBytes=20*1024*1024,
                              backupCount=5,
                              encoding=None,
                              delay=0)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

from time import sleep
from serial import Serial
import crc16
from struct import pack, unpack
import sys


if len(sys.argv) >= 2:
    address = int(sys.argv[1])
else:
    address = 176

hexString = lambda byteString : " ".join(x.encode('hex') for x in byteString)

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
    logger.debug("request:\t{}\tresponse:\t{}\t{}".format(hexString(rq),hexString(rs), crcCheck))
    return crcCheckOK, rs

rr_list = [
    "\x00", #echo
    "\x01\x01\x01\x01\x01\x01\x01\x01", #set connection via password
]

rq_dict = [
    # constants
    # {'rq': '\x08\x00',      'pos': 1, 'frame': '>7B', 'name': 'production time and date', },
    # {'rq': '\x08\x02',      'pos': 1, 'frame': '>2H', 'name': 'Ku Ki', },
    # {'rq': '\x08\x12',      'pos': 1, 'frame': '6I', 'name': 'model version', },
    # archive
    {'rq': '\x05\x00\x00',  'pos': 1, 'frame': '>4I', 'name': 'Ts', },
    {'rq': '\x05\x00\x01',  'pos': 1, 'frame': '>4I', 'name': 'T1', },
    {'rq': '\x05\x00\x02',  'pos': 1, 'frame': '>4I', 'name': 'T2', },
    {'rq': '\x05\x60\x00',  'pos': 1, 'frame': '>3I', 'name': 'Ts phase', },
    {'rq': '\x05\x60\x01',  'pos': 1, 'frame': '>3I', 'name': 'T1 phase', },
    {'rq': '\x05\x60\x02',  'pos': 1, 'frame': '>3I', 'name': 'T2 phase', },
    # instant
    {'rq': '\x08\x11\x00',  'pos': 2, 'frame': '<H', 'name': 'Ps/100', },
    {'rq': '\x08\x11\x01',  'pos': 2, 'frame': '<H', 'name': 'Pa/100', },
    {'rq': '\x08\x11\x02',  'pos': 2, 'frame': '<H', 'name': 'Pb/100', },
    {'rq': '\x08\x11\x03',  'pos': 2, 'frame': '<H', 'name': 'Pc/100', },
    {'rq': '\x08\x11\x11',  'pos': 2, 'frame': '<H', 'name': 'Ua/100', },
    {'rq': '\x08\x11\x12',  'pos': 2, 'frame': '<H', 'name': 'Ub/100', },
    {'rq': '\x08\x11\x13',  'pos': 2, 'frame': '<H', 'name': 'Uc/100', },
    {'rq': '\x08\x11\x21',  'pos': 2, 'frame': '<H', 'name': 'Ia/1000',},
    {'rq': '\x08\x11\x22',  'pos': 2, 'frame': '<H', 'name': 'Ib/1000',},
    {'rq': '\x08\x11\x23',  'pos': 2, 'frame': '<H', 'name': 'Ic/1000',},
    {'rq': '\x08\x11\x40',  'pos': 2, 'frame': '<H', 'name': 'Hz/100', },
    #{'rq': '\x04\x00',      'pos': 1, 'frame': '8B', 'name': 'Time and Date', },
]

def printAndAdd(bytes, rr_frame, name):
    if 'I' in rr_frame:
        l1 = len(bytes)
        if l1%4 == 0:
            len_div_4 = l1/4
            logger.info("{} :::: {}".format( name, unpack(">{}I".format(len_div_4),
                         pack('<{}h'.format(len_div_4*2), *unpack('>{}h'.format(len_div_4*2), bytes)))
                                             )
                        )
            b = ""
            for i in range(0, len(bytes), 4):
                b += bytesRearrange(bytes[i:i+4])
            return b
    else:
        logger.info("{} : {}".format(name, unpack(rr_frame, bytes))
                    )
        return bytes

def bytesRearrange(bytes):
    b = bytes[2]+bytes[3]+bytes[0]+bytes[1]
    return b

if __name__ == '__main__':
    logger.debug("Starting process with mercury addr = {} ...".format(address))

    ser = Serial(
        port='/dev/ttyUSB0',
        baudrate=9600,
        bytesize=8,
        parity='N',
        stopbits=1,
        timeout=0.5,
        xonxoff=0,
        rtscts=0
    )
    for i in range(2):
        logger.debug("trial {}".format(i))
        ser.open()

        #reset all data?
        ser.write('\x0f\x00\x00\x00')
        ser.read(size=100)

        for rr in rr_list:
            oneRXTX(address, rr)

        data = ""
        for d in rq_dict:
            checkOK, rs = oneRXTX(address,d['rq'])
            if checkOK:
                data += printAndAdd(bytes=rs[d['pos']:][:-2],
                                    rr_frame=d['frame'],
                                    name=d['name'] )

        ser.close()
        sleep(20)

    logger.debug("End process...")


