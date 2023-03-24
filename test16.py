import adc120sdk
import json
import time
from test_defs import *

print ("Test RJ 45")
print ("Collegare oscilloscopio a lemo base da 0 a 3 e applicare un segnale a ciascuna coppiola")
print ("Del connettore RJ-45")

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
        sdk.set_parameter("base.lemo.mode", "out", i)
    sdk.set_parameter("base.lemo.source", "rj45_lvds_0", 0)
    sdk.set_parameter("base.lemo.source", "rj45_lvds_1", 1)
    sdk.set_parameter("base.lemo.source", "rj45_lvds_2", 2)
    sdk.set_parameter("base.lemo.source", "rj45_lvds_3", 3)

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