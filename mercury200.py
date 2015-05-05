import serial
import crc16
import sys

# hex(intAddress)[2:].zfill(6).decode('hex')
# more intellegent
def convert(int_value):
   encoded = format(int_value, 'x')
   length = len(encoded)
   encoded = encoded.zfill(length+length%2)
   return encoded.decode('hex')
   
def oneRXTX(intAddress, strCmd):
	rq = '\x00'+convert(intAddress)+strCmd
	rq = rq + convert(crc16.calcString(rq, crc16.INITIAL_MODBUS))[::-1]
	ser.write(rq)
	rs = ser.read(size=100)
	if convert( crc16.calcString(rs[:-2], crc16.INITIAL_MODBUS) ) == rs[-2:][::-1]:
		crcCheck = "CRC OK"
	else:
		crcCheck = "CRC BAD!!!"
	print "request:\t", hexString(rq), "\nresponse:\t", hexString(rs), '\n',crcCheck


#if __name__ == '__main__': 

hexString = lambda byteString : " ".join(x.encode('hex') for x in byteString)

ser = serial.Serial(port='/dev/ttyUSB0', 
baudrate=9600, 
bytesize=8, 
parity='N', 
stopbits=1, 
timeout=0.3, 
xonxoff=0, 
rtscts=0)

#sample rq&rs
getPowerCRC = "\x00\x08\x11\xE1\x26\xBF\xEF"
ser.write(getPowerCRC)
response = ser.read(size=100)
hexString(response)

address = 528865
if len(sys.argv)==2:
	cmd = sys.argv[1]
else:
	cmd = '\x63'
oneRXTX(address,cmd)
