
import adc120sdk
import threading
import time
from DigitizerAnalogTraceMessage import DigitizerAnalogTraceMessage

import csv

import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

from threading import Thread, Lock


mutex = Lock()

dump_raw = False
dump = False
if dump==True:
    f = open('data_file.csv', 'w')
    writer = csv.writer(f)


    

DGZ_IP = ["tcp://192.168.102.117:5556"]
#DGZ_IP = ["tcp://d1.sw:10113"]

sdks = []
curve = []
p=[]
datas=[]


def thread_readout_function(sdk):
    cnt = 0
    global data_array
    while 1:
        message = sdk.get_data()
        fb = DigitizerAnalogTraceMessage.GetRootAsDigitizerAnalogTraceMessage(message)
        mutex.acquire()
        datas.clear()

        if dump_raw==True:
            fr = open('raw/data_file' + str(cnt) + '.raw', 'wb')
            fr.write(message)
            fr.close
        cnt = cnt +1
        sp = fb.Metadata()
        #print( sp.Timestamp().Nanosecond() )
        print( str(sp.Timestamp().Year())  + "/" + "/" +str(sp.Timestamp().Day())  + "  " + 
            str(sp.Timestamp().Hour())  + ":" + str(sp.Timestamp().Minute())  + ":" +str(sp.Timestamp().Second())  + "." + 
            str(sp.Timestamp().Millisecond())  + "-" + str(sp.Timestamp().Millisecond())  + "-" +str(sp.Timestamp().Nanosecond()) )
        print( sp.FrameNumber() )
        for i in range(0, fb.ChannelsLength()):
            timestamp =  fb.Channels(i).VoltageAsNumpy()
            data = fb.Channels(i).VoltageAsNumpy()
            #print(data)
            rms = np.sqrt(np.mean((data-np.mean(data))**2))/4096.0*1.34
            print(str(i) + " " + str(rms*1000) + "mV")
            datas.append(data)

            if dump==True:
                if (i==0):
                    writer.writerow(data)
        mutex.release()




for ip in DGZ_IP:
    sdks.append(adc120sdk.AdcControl())
    sdks[-1].connect_data(ip)


app = pg.mkQApp("Plotting Example")
win = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
win.resize(1000,600)    
pg.setConfigOptions(antialias=True)
for i in range(0, 8):
    p.append(win.addPlot(title=("ch" + str(i))))
    curve.append( p[i].plot(pen='y') )
    if (i % 2)==1:
        win.nextRow()

for idx, sdk in enumerate(sdks):
    threading.Thread(target=thread_readout_function, args=(sdk,)).start()

def update():
    
    mutex.acquire()
    q=0
    for i in datas:
        #z = np.convolve(i, np.ones(32)/32, mode='valid')
        curve[q].setData(i)
        q+=1
    mutex.release()

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(100)
pg.exec()


