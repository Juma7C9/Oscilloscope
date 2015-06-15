import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

import util
import serial_read as ser

app = QtGui.QApplication([])

#file = "../sample.dat"
#data = np.fromfile(file, dtype=np.uint8)

fromSerial = True

if( not fromSerial ):
	file = "../chunk.npy"
	data = np.load(file)
	chunk = 100000
else:
	chunk = 5000

win = pg.GraphicsWindow()
p1 = win.addPlot()
curve = p1.plot()

p1.setDownsampling(mode='peak')
p1.setClipToView(True)
p1.setRange(xRange=[-2, 0], yRange=[0,5])



x1 = np.zeros((0))
y1 = np.zeros((0))



i = 0
last_ovf = 0
skip = 0
def update():
	global i, x1, y1, last_ovf, skip
	if( fromSerial ):
		data = ser.read(chunk, skip)
		skip = util.findIndex( data ) % 4
		
		
	if i < data.size:
		if( not fromSerial ):
			end = min( i+chunk, data.size )
			(x, y, f0, f1, last_ovf) = util.fillDataPoints( data, start=i, end=end, time_ovf_count=last_ovf )
		else:
			(x, y, f0, f1, last_ovf) = util.fillDataPoints( data, time_ovf_count=last_ovf )
			
		time = 4*10**(-6)*x.astype(np.float) # Time resolution is 64*clk = 4 uS
		
		x1 = np.append(x1, time)
		y1 = np.append(y1, y)
		
		c = x1 > 0
		x2 = x1[c]
		y2 = y1[c]
		curve.setData(x=x2, y=y2*4.721e-3)
		curve.setPos(-x2[-1], 0)
		
		if( not fromSerial ):
			i += chunk
		
	else:
		timer.stop()
		stop_time = pg.ptime.time()
		
		print( x1[-1] )
		print( stop_time - start_time )

start_time = pg.ptime.time()
timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(60)

app.exec_()


