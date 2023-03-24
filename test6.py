import adc120sdk
import json
import time
from test_defs import *

print ("Questo test verifica i clock IN")
print ("Collegare un generatore di segnale al clock in")
print ("Verificare che il clock in appaia sul lemo clock out e sul lemo 0 della base")
print ("Verificare sul test point delle DAQ che il clock arrivi correttamente a tutti i distributor")
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
    sdk.set_parameter("base.common_clock.source", "clk_ext", 0)
    for i in range(0,16):
        sdk.set_parameter("base.lemo.mode", "out", i)
    sdk.set_parameter("base.lemo.source", "clk_in", 0)
    sdk.execute_cmd("configure_dgtz")
    sdk.execute_cmd("configure_base")

    time.sleep(1)
    p = sdk.get_parameter("system.clk.pllstatus", 0)
    str_p = str(p)
    print(str_p)
    if (str_p != "refa:ok;refb:ok;lock1:ok;lock2:ok;ref_sel:B;ref_missing:false;hovering:false"):
        failed = True
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