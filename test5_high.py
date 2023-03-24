import adc120sdk
import json
from test_defs import *

print ("Questo test verifica i lemo della BASE: tutti input")
print ("Collegare un generatore di segnale a ciascun input e verificare ")
print ("la frequenza sul display")
failed = False
sdk = adc120sdk.AdcControl()

ip = DGZ_IP[0]
try:
    sdk.connect(ip)
    print ("Digitizer %s connesso" % ip)
except:
    print ("Digitizer %s non raggiungibile" % ip)
    exit(-2)

try:
    for i in range(0,16):
        sdk.set_parameter("base.lemo.mode", "in_h", i)

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