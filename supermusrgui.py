import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *

from scisdk.scisdk import SciSDK
import math
import scipy.optimize as opt
import ctypes
from pyqtgraph.parametertree import Parameter, ParameterTree, parameterTypes
from DigitizerAnalogTraceMessage import DigitizerAnalogTraceMessage
from threading import Thread, Lock
import threading
import json
import adc120sdk
import time



CH_MAP = range(0,32)
DGZ_IP = ["tcp://192.168.102.177"]



sdks = []
dataw= []
p_w=[]
curve_w = []
datas= []
p_s=[]
curve_s = []
data_tof= []
p_tof=[]
curve_tof = []

acq_thread_list = []

dataw_valid=False
mutex = Lock()
 

for ip in DGZ_IP:
    sdks.append(adc120sdk.AdcControl())
    sdks[-1].connect(ip + ":5557")
    sdks[-1].connect_data(ip + ":5556")
    sdks[-1].set_timeout(2000)

 

#for each connected digitizer

for idx, sdk in enumerate(sdks):
    try:
        sdk.execute_cmd("stop_acquisition") #always stop before changing anthing!
    except:
        print ("Digitized is not running")

    s=sdk.get_parameter("dgtz.info.section")
    section = int(float(s))
    sn = sdk.get_parameter("system.serialnumber")
    swver = sdk.get_parameter("system.swversion")
    compile_data = sdk.get_parameter("system.compile_data")
    fwver = sdk.get_parameter("dgtz.probes.fwver")


    print("sn: " + sn + "  section: " + str(section))
    print("SW-VER: " + swver + " (" + compile_data + ")  -- FPGA-VER: "  + fwver)


app = pg.mkQApp("SuperMUSR GUI")
window = QMainWindow()
window.setWindowTitle('SuperMUSR GUI')


def create_params(json_data, parent_name=''):
    params = []
    for key, value in json_data.items():
        param_name = f"{parent_name}.{key}" if parent_name else key
        if isinstance(value, dict):
            # Check for nested dictionaries
            if 'type' in value:
                # Normal parameter
                if 'count' in value:
                    # Replicate this parameter 'count' times
                    children = [create_param(value, index=i) for i in range(value['count'])]
                    params.append({'name': key, 'type': 'group', 'children': children, 'expanded': False})
                elif 'replicate' in value:
                    # Single parameter, but replicated on apply
                    params.append(create_param(value, replicate=True))
                else:
                    params.append(create_param(value))
            else:
                # Nested group of parameters
                children = create_params(value, parent_name=param_name)
                params.append({'name': key, 'type': 'group', 'children': children, 'expanded': False})
    return params

def create_param(value, index=None, replicate=False):
    param_info = {'name': value['command']+":" + str(index) if index is not None else value['command'], 'type': value['type'], 'value': value['value']}
    if value['type'] == 'list':
        param_info['values'] = value['values']
    param_info['index'] = index
    param_info['command'] = value['command']
    if replicate:
        param_info['replicate'] = True
        param_info['replicate_count'] = value['replicate']
    return param_info

def apply_settings(params, sdk):
    for param in params:
        if param.type() == 'group':
            apply_settings(param.children(), sdk)
        else:
            command = param.opts.get('command', "")
            value = param.opts.get('value', "0")
            if param.opts.get('replicate', False):
                count = param.opts.get('replicate_count', 1)
                for i in range(count):
                    try:
                        print("Setting parameter: " + command + " -> " + str(value) + " [" + str(i) +"]")
                        sdk.set_parameter(command, value, i)
                    except Exception as e:
                        print("Error setting parameter: " + command + " -> " + str(value) + " [" + str(i) +"]")
                        print(e.args[0]["message"])
                    
            else:
                index = param.opts.get('index', None)
                if index is not None:
                    try:
                        print("Setting parameter: " + command + " -> " + str(value) + " [" + str(index) +"]")
                        sdk.set_parameter(command, value, index)
                    except Exception as e:
                        print("Error setting parameter: " + command + " -> " + str(value) + " [" + str(index) +"]")
                        print(e.args[0]["message"])
                else:
                    try:
                        print("Setting parameter: " + command + " -> " + str(value) )
                        sdk.set_parameter(command, value)
                    except Exception as e:
                        print("Error setting parameter: " + command + " -> " + str(value) )
                        print(e.args[0]["message"])

def program_settings(params, sdk):
    apply_settings(params, sdk)
    sdk.execute_cmd("configure_dgtz")
    sdk.execute_cmd("configure_base")
    try:
        sdk.execute_cmd("configure_hv")
    except Exception as e:
        print("Error executing HV programming:" + str(e))

    try:
        sdk.execute_cmd("configure_staves")
    except Exception as e:
        print("Error executing stave programming:" + str(e))

    sdk.execute_cmd("reset_darkcount_spectra")           



def save_settings_to_file(params, filename):
    settings = {}
    def extract_params(params, container):
        for param in params:
            if param.type() == 'group':
                container[param.name()] = {}
                extract_params(param.children(), container[param.name()])
            else:
                container[param.name()] = param.value()

    extract_params(params, settings)
    with open(filename, 'w') as file:
        json.dump(settings, file, indent=4)


def save_settings_with_dialog(params, parent_widget):
    filename, _ = QFileDialog.getSaveFileName(parent_widget, "Save Settings", "", "JSON Files (*.json)")
    if filename:
        save_settings_to_file(params, filename)


def load_settings_from_file(params, filename):
    with open(filename, 'r') as file:
        settings = json.load(file)

    def apply_params(params, settings):
        for param in params:
            if param.type() == 'group':
                apply_params(param.children(), settings.get(param.name(), {}))
            else:
                if param.name() in settings:
                    param.setValue(settings[param.name()])

    apply_params(params, settings)

def load_settings_with_dialog(params, parent_widget):
    filename, _ = QFileDialog.getOpenFileName(parent_widget, "Load Settings", "", "JSON Files (*.json)")
    if filename:
        load_settings_from_file(params, filename)

# Usage: load_settings_from_file(params.children(), 'settings.json')

# Main application setup

#load settings from json file

with open('parameters.json') as f:
    settings_json = json.load(f)

# Create ParameterTree
pt = pg.parametertree.ParameterTree()
root_params = create_params(settings_json)
params = pg.parametertree.Parameter.create(name='Settings', type='group', children=root_params)
pt.setParameters(params, showTop=True)
pt.setFixedWidth(400)

# Create start, stop, and reset buttons
apply_btn = QPushButton('Apply')

apply_btn.clicked.connect(lambda: program_settings(params.children(), sdk))

start_btn = QPushButton('Start')
stop_btn = QPushButton('Stop')
reset_btn = QPushButton('Reset')
save_btn = QPushButton('Save')
# Button for saving settings with file dialog
save_button = QPushButton("Save Settings")
save_button.clicked.connect(lambda: save_settings_with_dialog(params.children(), window))


# Button for loading settings with file dialog
load_button = QPushButton("Load Settings")
load_button.clicked.connect(lambda: load_settings_with_dialog(params.children(), window))
# Create plot widget



# Add plot widget and buttons to vertical layout
center_layout = QVBoxLayout()
button_layout = QHBoxLayout()
button_layout.addWidget(apply_btn)
button_layout.addWidget(load_button)
button_layout.addWidget(save_button)
button_layout.addWidget(start_btn)
button_layout.addWidget(stop_btn)
button_layout.addWidget(reset_btn)
button_layout.addWidget(save_btn)
center_layout.addLayout(button_layout)

plots_layout = QGridLayout()
tab_plot_widget = QTabWidget()
plots_layout.addWidget(tab_plot_widget, 0, 0)
center_layout.addLayout(plots_layout)

warea = pg.GraphicsLayoutWidget(show=True, title="Plot waveform (ZMQ push)")
tab_plot_widget.addTab(warea, "Waves")
for i in range(0, 8):
    p_w.append(warea.addPlot(title=("ch" + str(i))))
    curve_w.append( p_w[i].plot(pen='y') )
    if (i % 2)==1:
        warea.nextRow()


sarea = pg.GraphicsLayoutWidget(show=True, title="Plot spectrum (ZMQ pull)")
tab_plot_widget.addTab(sarea, "Spectra")
for i in range(0, 8):
    p_s.append(sarea.addPlot(title=("ch" + str(i))))
    curve_s.append( p_s[i].plot(pen='y') )
    if (i % 2)==1:
        sarea.nextRow()        

tof_area = pg.GraphicsLayoutWidget(show=True, title="Plot Toff (ZMQ pull)")
tab_plot_widget.addTab(tof_area, "TOF")
for i in range(0, 8):
    p_tof.append(tof_area.addPlot(title=("ch" + str(i))))
    curve_tof.append( p_tof[i].plot(pen='y') )
    if (i % 2)==1:
        tof_area.nextRow()     


# Create horizontal layout to add parameter tree and vertical layout
h_layout = QHBoxLayout()
h_layout.addWidget(pt)
h_layout.addLayout(center_layout)

# Create QWidget to hold the horizontal layout
widget = QWidget()
widget.setLayout(h_layout)



window.setCentralWidget(widget)
# Show widget
window.show()


def update_plot():
    global dataw_valid
    mutex.acquire()
    q=0
    for i in dataw:
        curve_w[q].setData(i)
        q+=1

    q=0
    for i in datas:
        curve_s[q].setData(i)
        q+=1    

    q=0
    for i in data_tof:
        curve_tof[q].setData(i)
        q+=1            
    datas.clear()    
    dataw_valid=False
    mutex.release()
    

# Create a timer object and set its interval
timer = QtCore.QTimer()
timer.timeout.connect(update_plot)
#update_plot(obSpectrum)

timer.start(500) # Update the plot every 10 ms

running = False

def thread_readout_wave_function(sdk):
    global dataw_valid
    global running
    while running:
        try:
            message = sdk.get_data()
            fb = DigitizerAnalogTraceMessage.GetRootAsDigitizerAnalogTraceMessage(message)
            sp = fb.Metadata()
            if dataw_valid==False:
                mutex.acquire()
                dataw.clear()
                for i in range(0, fb.ChannelsLength()):
                    timestamp =  fb.Channels(i).VoltageAsNumpy()
                    data = fb.Channels(i).VoltageAsNumpy()
                    dataw.append(data)
                dataw_valid=True
                mutex.release()    
        except Exception as e:
            # jost do nothing
            pass
            

def thread_readout_spectrum_function(sdk):
    global running
    while running:
        try:
            spectra = sdk.read_data("get_A_spectra")
            mutex.acquire()
            datas.clear()
            for i in range(0, len(spectra)):
                datas.append(spectra[i])
            mutex.release()
        except Exception as e:
            # jost do nothing
            pass
        
        time.sleep(1)

def thread_readout_hist_tof_function(sdk):
    global running
    while running:
        try:
            hist_tof = sdk.read_data("get_tof_spectra")
            mutex.acquire()
            data_tof.clear()
            for i in range(0, len(hist_tof)):
                data_tof.append(hist_tof[i])
            mutex.release()
        except Exception as e:
            # jost do nothing
            pass
        
        time.sleep(1)


def start_thread_readout():
    global sdks
    global running
    global acq_thread_list
    if running == False:
        running = True
    try :
        for idx, sdk in enumerate(sdks):
            sdk.execute_cmd("reset_darkcount_spectra")
            sdk.execute_cmd("reset_tof_spectra")
            sdk.execute_cmd("start_acquisition")
    except Exception as e:
        print(str(e))

    for idx, sdk in enumerate(sdks):
        tw = threading.Thread(target=thread_readout_wave_function, args=(sdk,))
        tw.start()
        acq_thread_list.append(tw)
        ts = threading.Thread(target=thread_readout_spectrum_function, args=(sdk,))
        ts.start()
        acq_thread_list.append(ts)
        ts = threading.Thread(target=thread_readout_hist_tof_function, args=(sdk,))
        ts.start()
        acq_thread_list.append(ts)

def stop_thread_readout():
    global sdks
    global running
    global acq_thread_list
    running = False
    for t in acq_thread_list:
        t.join(5)

    try :
        for idx, sdk in enumerate(sdks):
            sdk.execute_cmd("stop_acquisition")
    except Exception as e:
        print(str(e))


start_btn.clicked.connect(lambda: start_thread_readout())
stop_btn.clicked.connect(lambda: stop_thread_readout())

def reset_histograms():
    global sdks
    for idx, sdk in enumerate(sdks):
        sdk.execute_cmd("reset_darkcount_spectra")
        sdk.execute_cmd("reset_tof_spectra")

reset_btn.clicked.connect(lambda: reset_histograms())
if __name__ == '__main__':
    pg.setConfigOption("useOpenGL", True)
    pg.setConfigOption("useNumba", True)
    pg.setConfigOption("useCupy", True)

    pg.exec()

    #app.exec_()