import adc120sdk
import json
from test_defs import *

print ("Questo test verifica i lemo del DAQ: lemo 0 uscita e lemo 1 uscita")
print ("Verificare la presenza di un segnale a 50 Hz su entrabe i lemo")
failed = False
sdks = []

test_report = []
i=0
for ip in DGZ_IP:
    sdks.append(adc120sdk.AdcControl())
    try:
        sdks[-1].connect(ip)
        print ("Digitizer %s connesso" % ip)
        test_report["dgtz"][i]["connection"] = True
    except:
        print ("Digitizer %s non raggiungibile" % ip)
        sdks.pop()
        failed = True
    
for sdk in sdks:
    try:
        sdk.set_parameter("trg.self_rate", 50)
        sdk.set_parameter("trg.mode", "periodic")
        sdk.set_parameter("dgtz.lemo.mode", "out", 0)
        sdk.set_parameter("dgtz.lemo.mode", "out", 1)
        sdk.set_parameter("dgtz.lemo.source", "trigger_out", 0)
        sdk.set_parameter("dgtz.lemo.source", "trigger_out", 1)

        sdk.execute_cmd("configure_dgtz")
    except:
        #print error mesagge and which function generate it
        print ("Errore durante la lettura dei parametri")
        failed = True
        
    i=i+1


# salva il report in json
with open('test_report.json', 'w') as outfile:
    json.dump(test_report, outfile)

if failed:
    print ("Test fallito")
    exit(-1)
else:
    print ("Test completato")