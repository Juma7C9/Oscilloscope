import numpy as np

# Off = 0, Error = 1, Warning = 2, Verbose = 3, VeryVerbose = 4, VeryVeryVerbose = 5
max_debug_level = 3
np.set_printoptions(threshold=1000000)


def debug( *args, debuglevel=4):
	if debuglevel <= max_debug_level:
		print( *args )

def xor( array ):
	debug("xor( ", array, " )", debuglevel=4)
	a = array
	try:
		base = a[0]^a[1]^a[2]^a[3]
		_xor = (base>>4)^(base&15)
	except IndexError:
		debug("[ERROR]: XOR out of bounds", debuglevel=1)
		_xor = 1 # In case of error, return _xor != 0
	debug("_xor ", _xor, debuglevel=3)
	return _xor

def sumXor( data, index=0, steps=500 ):
	debug("sumXor( ", data, index, steps, " )", debuglevel=4)
	sum_xor = 0
	last = min(index+steps, data.size)
	for i in range( index, last, 4):
		_xor = xor( data[i:i+4] )
		sum_xor += _xor
	debug( sum_xor )
	return sum_xor


def findIndex( data, ind=0 ):
	debug("findIndex( ", data, ind, " )", debuglevel=4)
	indexFound = False
	
	while not indexFound:
		if sumXor( data, ind ) == 0:
			indexFound = True
		else:
			ind += 1
	debug( ind , debuglevel=3)
	return ind

#@profile
def fillDataPoints( data, start=0, end=0, time_ovf_count=0 ):
	if( end == 0 ):
		end=data.size
	
	debug("fillDataPoints( ", data, start, end, " )", debuglevel=4)
	startIndex = findIndex( data, start )
	debug("startIndex( ", startIndex, " )", debuglevel=3)
	maxvalue = (end - startIndex)//4
	data_r = data[startIndex:startIndex+4*maxvalue].reshape((-1,4))

	maxfails = 1
	fails = 0

	timestamp = np.zeros((maxvalue), dtype=np.uint32) # end - startIndex
	value = np.zeros((maxvalue), dtype=np.uint16)
	flag0 = np.zeros((maxvalue), dtype=np.uint8)
	flag1 = np.zeros((maxvalue), dtype=np.uint8)
	
	#time_ovf_count = 0
	i = 0
	while i < data_r.shape[0]:
		if xor( data_r[i] ) == 0:
			orig_time = (data_r[i,0]*256) + (data_r[i,1])
			if (i > 0) and ((time_ovf_count*2**16 + orig_time) < timestamp[i-1]):
				time_ovf_count += 1
			timestamp[i] = time_ovf_count*2**16 + orig_time
			value[i] = data_r[i,2]*4 + data_r[i,3]//64
			flag0[i] = data_r[i,3]&(1<<5)
			flag1[i] = data_r[i,3]&(1<<4)
		elif fails > maxfails:
			debug("[ERROR] Index lost on pos ", i, ", recounting.", debuglevel = 1)
			i = findIndex( data, i )
			debug("\t New pos: ", i, debuglevel = 2)
			fails = 0
		else:
			fails += 1
	
		i += 1

	debug( timestamp, value, flag0, flag1, debuglevel=3 )
	return timestamp, value, flag0, flag1, time_ovf_count

