import adc120sdk
import json
import time
from test_defs import *

print ("Test ADC SYNC")
print ("Applicare un segnale al lemo 0 della base e verificare che il segnale")
print ("sia presente sul lemo 0 di ogni DAQ e su lemo 1 della base.")
sdks = []
failed = False
for ip in DGZ_IP:
    sdks.append(adc120sdk.AdcControl())
    try:
        sdks[-1].connect(ip)
        print ("Digitizer %s connesso" % ip)
    except:
        print ("Digitizer %s non raggiungibile" % ip)
        sdks.pop()
        failed = True

for sdk in sdks:
    try:

        sdk.set_parameter("base.lemo.mode", "in_h", 0)
        sdk.set_parameter("base.lemo.mode", "out", 1)
        sdk.set_parameter("base.adc_sync.source", "lemo_0", 0)
        sdk.set_parameter("base.lemo.source", "adc_sync", 1)

        sdk.set_parameter("dgtz.lemo.mode", "out", 0)
        sdk.set_parameter("dgtz.lemo.source", "adc_sync", 0)
        sdk.set_parameter("dgtz.lemo.mode", "out", 1)
        sdk.set_parameter("dgtz.lemo.source", "adc_sync", 1)

        sdk.execute_cmd("configure_dgtz")
        sdk.execute_cmd("configure_base")

    except:
        #print error message and which function generate it
        print ("Errore durante la lettura dei parametri")
        failed = True
    
if failed:
    print ("Test fallito")
    exit(-1)
else:
    print ("Test completato")
    exit(0)