import numpy as np
import serial
import atexit

from util import debug

chunk_size = 1000

data = np.zeros((chunk_size), dtype=np.uint8)
outfile = "../chunk.npy"

ser = serial.Serial()

ser.port = '/dev/ttyACM0'
ser.baudrate = 500000
ser.open()

def read(size, skip=0):
	ser.read(skip)
	return np.frombuffer( ser.read(size), dtype=np.uint8 )

def async_read(pipe, size):
	try:
		while(True):
			pipe.send( np.frombuffer(ser.read(size), dtype=np.uint8) )
			skip = pipe.recv()
			ser.read(skip)
			if( not skip == 0 ):
				debug("Skipped ", skip, debuglevel=3)
			
	except SystemExit:
		pipe.close()
		ser.close()
	
atexit.register(ser.close)

# Stand-alone behaviour
if __name__ == '__main__':
	try:
		data = np.frombuffer( ser.read(chunk_size), dtype=np.uint8 )
		while( True ):
			while( ser.inWaiting() == 0 ):
				pass
				
			raw_data = ser.read( chunk_size )
			data_new = np.frombuffer( raw_data, dtype=np.uint8 )
			
			data = np.append(data, data_new)

			print( data_new )
			
	except KeyboardInterrupt:
		ser.close()
		np.save(outfile, data)
		
		print("\n\n\n\n\n\n")
		print(data)
		print("Exit")


