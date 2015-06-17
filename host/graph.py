import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
#import pyqtgraph.widgets.RemoteGraphicsView

from multiprocessing import Process, Pipe

import time as tm
from tempfile import TemporaryDirectory

#import pyximport; pyximport.install()
import c_util as util
from util import debug
#import util
import serial_read as ser

app = QtGui.QApplication([])
pg.setConfigOptions(antialias=True)
#view = pg.widgets.RemoteGraphicsView.RemoteGraphicsView()

#file = "../sample.dat"
#data = np.fromfile(file, dtype=np.uint8)

fromSerial = True

if( not fromSerial ):
	file = "../chunk.npy"
	datafile = np.load(file)
	chunk = 100000
else:
	chunk = 5000

#plot = pg.GraphicsWindow()
#plot = view.pg.GraphicsWindow()
#plot._setProxyOptions(deferGetattr=True)

p1 = pg.PlotWidget()

layout = pg.LayoutWidget()
layout.addWidget(p1, row=1, col=0, rowspan=2)

pause_b = QtGui.QCheckBox('Pause')

layout.addWidget(pause_b, row=0, col=0)
layout.show()

#p1 = plot.addPlot()
p1.showGrid(x=True, y=True)
curve = p1.plot()

#p1.setDownsampling(mode='peak')
#p1.setClipToView(True)
p1.setRange(xRange=[-2, 0], yRange=[0,5])

tmpdir = TemporaryDirectory()
debug("Temporary directory is: %s" % tmpdir.name, debuglevel=3)

x1 = np.zeros((0))
y1 = np.zeros((0))

if( fromSerial ):
	(child_p, parent_p) = Pipe()
	reader = Process(target=ser.async_read, args=(child_p, chunk))
	reader.start()

i = 0
last_ovf = 0
skip = 0
def update_data():
	global i, x1, y1, last_ovf, skip
	maxpts = 200000		# Datapoints to be shown on graph
	maxsize = 500000	# Datapoints to be kept in memory
	
	try:
		if( fromSerial ):
			#data = ser.read(chunk, skip)
			#skip = util.findIndex( data ) % 4
			
			data = parent_p.recv()
			skip = util.findIndex( data ) % 4
			parent_p.send(skip)
		else:
			data = datafile
			
		if i < data.size:
			if( not fromSerial ):
				end = min( i+chunk, data.size )
				(x, y, f0, f1, last_ovf) = util.fillDataPoints( data, start=i, end=end, time_ovf_count=last_ovf )
			else:
				(x, y, f0, f1, last_ovf) = util.fillDataPoints( data, time_ovf_count=last_ovf )
				
			time = 4*10**(-6)*x.astype(np.float) # Time resolution is 64*clk = 4 uS
			
			if( x1.size > maxsize ):
				temp_x = x1[-maxsize//2:].copy() # Preserve second (newest) half
				temp_y = y1[-maxsize//2:].copy()
				
				# Save first (oldest) half
				now = tm.localtime(tm.time())
				tempfile = "%s/tmp_%d-%.2d-%.2d_%.2d.%.2d.%.2d.npz" % (	
							tmpdir.name, now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
				np.savez_compressed(tempfile, x1[:maxsize//2], y1[:maxsize//2])
				debug("Tempfile %s created" % (tempfile), debuglevel=3)
				
				x1 = temp_x
				y1 = temp_y
				
			x1 = np.append(x1, time)
			y1 = np.append(y1, y)
			
			level = 500
			direction = 'up'
			
			if( pause_b.isChecked() == False ):
				center = trigger(x1[-10000:-6000], y1[-10000:-6000], level, direction)
				if( not center == None ):
					update_graph(x1, y1, center, winsize=16000)
				#update_graph_trace(x1, y1, maxpts)
			
			if( not fromSerial ):
				i += chunk
			
		else:
			timer.stop()
			stop_time = pg.ptime.time()
			
			debug("Last time [s]: ", x1[-1], debuglevel=3)
			debug("Time to display [s]: ", stop_time - start_time, debuglevel=3)
			
	except KeyboardInterrupt:
		timer.stop()
		if( fromSerial ):
			reader.join()
		raise SystemExit

def update_graph(x, y, center, winsize=10000):
	c = x > 0
	x_g = x[c]
	y_g = y[c]
	
	curve.setData(x=x_g[-winsize:], y=y_g[-winsize:]*4.721e-3)
	curve.setPos(-center, 0)
	

def update_graph_trace(x, y, maxpts=200000):
	c = x > 0
	x_g = x[c]
	y_g = y[c]
	curve.setData(x=x_g[-maxpts:], y=y_g[-maxpts:]*4.721e-3)
	curve.setPos(-x_g[-1], 0)
	
def trigger(x, y, level, direction):
	'''
	We want to find the position in which the signal crosses the
	threshold, so we search for the first index higher (or lower)
	than the threshold. If the position corrensponds to the first
	index we discard it, as it means that the beginning *altready*
	was over the threshold, and it is not the correct position.
	'''
	try:
		if( direction == 'up' ):
			ind = np.argmax( y>level )
			if(ind == 0):
				ind = np.argmax((y>level)[np.argmax(y<level):]) + np.argmax(y<level)
		elif( direction == 'down' ):
			ind = np.argmax( y<level )
			if(ind == 0):
				ind = np.argmax((y<level)[np.argmax(y>level):]) + np.argmax(y>level)
		else:
			raise KeyError("direction must be 'up' or 'down'")
			
		return x[ind]
		
	# If the sequence passed to argmax() is empty an exception is raised
	except (ValueError, UnboundLocalError) as e:
		debug("[Warning] %s: %s" % (e.__class__.__name__, e), debuglevel=2)
	

start_time = pg.ptime.time()
timer = pg.QtCore.QTimer()
timer.timeout.connect(update_data)
timer.start(50)


'''
j=0
while(j<100):
	update_data()
	j+=1
'''

app.exec_()


