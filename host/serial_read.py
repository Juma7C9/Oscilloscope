import numpy as np
import serial
import atexit

chunk_size = 1000

data = np.zeros((chunk_size), dtype=np.uint8)
outfile = "../chunk.npy"

ser = serial.Serial()

ser.port = '/dev/ttyACM1'
ser.baudrate = 500000
ser.open()

def read(size, skip=0):
	ser.read(skip)
	return np.frombuffer( ser.read(size), dtype=np.uint8 )

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


