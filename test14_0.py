import adc120sdk
import json
import time
from test_defs import *

print ("Spegne alimentazione di tutte le stave")

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
    sdk.set_parameter("base.stave.power", "false", 0)
    sdk.execute_cmd("configure_base")
    
except:
    #print error mesagge and which function generate it
    print ("Errore durante la lettura dei parametri")
    failed = True
    