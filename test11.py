import adc120sdk
import json
from test_defs import *

print ("Verifica distribuzione dei Sync OUT della DAQ D")
print ("Verificare che con un oscilloscopio che sulla base dal lemo 0 a 7 appaia un segnale a 176Hz")

failed = False
sdk = adc120sdk.AdcControl()
test_report = []
i=0
ip = DGZ_IP[3]
try:
    sdk.connect(ip)
    print ("Digitizer %s connesso" % ip)
    test_report["dgtz"][i]["connection"] = True
except:
    print ("Digitizer %s non raggiungibile" % ip)
    exit(-2)


try:
  
    for i in range(0,16):
        sdk.set_parameter("base.lemo.mode", "out", i)

    sdk.set_parameter("base.lemo.source", "sync_d_0", 0)
    sdk.set_parameter("base.lemo.source", "sync_d_1", 1)
    sdk.set_parameter("base.lemo.source", "sync_d_2", 2)
    sdk.set_parameter("base.lemo.source", "sync_d_3", 3)
    sdk.set_parameter("base.lemo.source", "sync_d_4", 4)
    sdk.set_parameter("base.lemo.source", "sync_d_5", 5)
    sdk.set_parameter("base.lemo.source", "sync_d_6", 6)
    sdk.set_parameter("base.lemo.source", "sync_d_7", 7)

    for i in range(0,8):
        sdk.set_parameter("dgtz.sync.outmode", "t0_out", i)
    
    sdk.set_parameter("trg.mode", "periodic")
    sdk.set_parameter("trg.self_rate", 176)

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