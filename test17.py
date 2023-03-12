import adc120sdk
import json
import time
from test_defs import *

print ("Test ADC SYNC")
print ("Applicare un segnale al lemo 0 della base e verificare sul test point della DAQ la presenza di quel segnale")
print ("Per ogni DAQ. Il segnale è anche presente per verifica su lemo 1 della base")

failed = False
sdk = adc120sdk.AdcControl()
test_report = []
i=0
ip = DGZ_IP[0]
try:
    sdk.connect(ip)
    print ("Digitizer %s connesso" % ip)
    test_report["dgtz"][i]["connection"] = True
except:
    print ("Digitizer %s non raggiungibile" % ip)
    exit(-2)


try:

    sdk.set_parameter("base.lemo.mode", "in", 0)
    sdk.set_parameter("base.lemo.mode", "out", 1)
    sdk.set_parameter("base.adc_sync.source", "lemo_0", 0)
    sdk.set_parameter("base.lemo.source", "adc_sync", 1)

    sdk.execute_cmd("configure_dgtz")
except:
    #print error mesagge and which function generate it
    print ("Errore durante la lettura dei parametri")
    failed = True
    
  


# salva il report in json
with open('test_report.json', 'w') as outfile:
    json.dump(test_report, outfile)

if failed:
    print ("Test fallito")
    exit(-1)
else:
    print ("Test completato")