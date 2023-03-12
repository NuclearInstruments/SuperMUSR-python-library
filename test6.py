import adc120sdk
import json
from test_defs import *

print ("Questo test verifica i clock IN")
print ("Verificare che il clock in appaia sul lemo clock out e sul lemo 0 della base")
print ("Verificare sul test point delle DAQ che il clock arrivi correttamente a tutti i distributor")
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
    sdk.set_parameter("base.common_clock.source", "clk_ext", 0)
    for i in range(0,16):
        sdk.set_parameter("base.lemo.mode", "out", i)
    sdk.set_parameter("base.lemo.source", "clk_in", 0)
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