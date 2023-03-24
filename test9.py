import adc120sdk
import json
from test_defs import *

print ("Verifica distribuzione dei Sync OUT della DAQ B")
print ("Verificare che con un oscilloscopio che sulla base dal lemo 0 a 7 appaia un segnale a 66Hz")

failed = False
sdk = adc120sdk.AdcControl()

ip = DGZ_IP[1]
try:
    sdk.connect(ip)
    print ("Digitizer %s connesso" % ip)
except:
    print ("Digitizer %s non raggiungibile" % ip)
    exit(-2)


try:
  
    for i in range(0,16):
        sdk.set_parameter("base.lemo.mode", "out", i)

    sdk.set_parameter("base.lemo.source", "sync_b_0", 0)
    sdk.set_parameter("base.lemo.source", "sync_b_1", 1)
    sdk.set_parameter("base.lemo.source", "sync_b_2", 2)
    sdk.set_parameter("base.lemo.source", "sync_b_3", 3)
    sdk.set_parameter("base.lemo.source", "sync_b_4", 4)
    sdk.set_parameter("base.lemo.source", "sync_b_5", 5)
    sdk.set_parameter("base.lemo.source", "sync_b_6", 6)
    sdk.set_parameter("base.lemo.source", "sync_b_7", 7)

    for i in range(0,8):
        sdk.set_parameter("dgtz.sync.outmode", "trigger_out", i)
        sdk.set_parameter("trg.threshold", 2000, i)

    sdk.set_parameter("trg.mode", "periodic")
    sdk.set_parameter("trg.self_rate", 66)

    sdk.execute_cmd("configure_dgtz")
    sdk.execute_cmd("configure_base")
except:
    #print error mesagge and which function generate it
    print ("Errore durante la lettura dei parametri")
    failed = True
    
if failed:
    print ("Test fallito")
    exit(-1)
else:
    print ("Test completato")
    exit(0)