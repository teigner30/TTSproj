import serial, time, sys

try:
	usb = serial.Serial('/dev/ttyACM0')
	print(usb.name)
	print(usb.baudrate)
except:
	try:
		usb = serial.Serial('/dev/ttyACM1')
		print(usb.name)


		print(usb.baudrate)
	except:
		print("No servor serial ports found")
		sys.exit(0)

target = 6000

lsb = target &0x7F
msb = (target >> 7) & 0x7F

cmd = chr(0xaa) + chr(0xC) + chr(0x04) + chr(0x01) + chr(lsb) + chr(msb)

#0x00 - waist
#0x01 - wheel speed
#0x02 - wheel direction
#0x03 - head yaw
#0x04 - head pitch

print("Writing")
usb.write(cmd.encode('utf-8'))
print("reading")
