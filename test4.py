import adc120sdk
import json
from test_defs import *

print ("Questo test verifica i lemo della BASE: lemo tutte uscite")
print ("Verificare con l'oscilloscopio la presenza di un segnale a 100KHz")
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

    for i in range(0,16):
        sdk.set_parameter("base.lemo.source", "pulse_gen", i)   

    sdk.set_parameter("base.pulsegen.freq", 100000.0, 0)

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