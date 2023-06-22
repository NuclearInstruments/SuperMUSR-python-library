
import adc120sdk
import threading
import time
from DigitizerAnalogTraceMessage import DigitizerAnalogTraceMessage


import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

from threading import Thread, Lock

mutex = Lock()


DGZ_IP = ["tcp://192.168.102.117:5557"]
#DGZ_IP = ["tcp://d1.sw:10112"]

sdks = []
curve = []
p=[]
datas=[]


def thread_readout_function(sdk):
    global data_array
    while 1:
        spectra = sdk.read_data("get_tof_spectra")
        mutex.acquire()
        datas.clear()
        for i in range(0, len(spectra)):
            datas.append(spectra[i])
        mutex.release()
        time.sleep(1)




for ip in DGZ_IP:
    sdks.append(adc120sdk.AdcControl())
    sdks[-1].connect(ip)


app = pg.mkQApp("SuperMUSR UI")
win = pg.GraphicsLayoutWidget(show=True, title="Spectrum Plotting Polling")
win.resize(1000,600)    
pg.setConfigOptions(antialias=True)

for i in range(0, 8):
    p.append(win.addPlot(title=("ch" + str(i)) ))
    curve.append( p[i].plot(pen='y') )

    if (i % 2)==1:
        win.nextRow()

for idx, sdk in enumerate(sdks):
    sdk.execute_cmd("reset_tof_spectra", 0)
    threading.Thread(target=thread_readout_function, args=(sdk,)).start()

def update():
    
    mutex.acquire()
    q=0
    for i in datas:
        curve[q].setData(i)
        q+=1
    mutex.release()

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(1000)
pg.exec()
exit(0)


