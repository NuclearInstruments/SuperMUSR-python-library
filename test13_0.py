import adc120sdk
import json
import time
from test_defs import *

print ("Verifica distribuzione dell'HV dei moduli 2 e 3 (DAQ C)")
print ("Verificare con un multimetro la presenza di 47V su HV 2 e 56V su HV 3")

failed = False
sdk = adc120sdk.AdcControl()
hv=[]

ip = DGZ_IP[2]
try:
    sdk.connect(ip)
    print ("Digitizer %s connesso" % ip)
except:
    print ("Digitizer %s non raggiungibile" % ip)
    exit(-2)

try:
    sdk.set_parameter("stave.BIAS.enable", "false",0)
    sdk.set_parameter("stave.BIAS.enable", "false",1)
    sdk.execute_cmd("configure_hv") 

except:
    #print error mesagge and which function generate it
    print ("Errore durante la lettura dei parametri")
    failed = True

sdk = adc120sdk.AdcControl()
ip = DGZ_IP[2]
try:
    sdk.connect(ip)
    print ("Digitizer %s connesso" % ip)
except:
    print ("Digitizer %s non raggiungibile" % ip)
    exit(-2)

try:
    sdk.set_parameter("stave.BIAS.enable", "false",0)
    sdk.set_parameter("stave.BIAS.enable", "false",1)
    sdk.execute_cmd("configure_hv") 

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