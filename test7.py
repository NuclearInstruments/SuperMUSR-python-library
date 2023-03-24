import adc120sdk
import json
from test_defs import *

print ("Verifica distribuzione del T0")
print ("Applicare T0 sul lemo 0 della base e verificare con un oscilloscopio che il T0")
print ("Appaia sul lemo 0 e 1 di tutte le DAQ")
failed = False
sdks = []

for ip in DGZ_IP:
    sdks.append(adc120sdk.AdcControl())
    try:
        sdks[-1].connect(ip)
        print ("Digitizer %s connesso" % ip)
    except:
        print ("Digitizer %s non raggiungibile" % ip)
        sdks.pop()
        failed = True

try:
    sdk=sdks[0]
    sdk.set_parameter("base.common_clock.source", "clk_int", 0)
  
    for i in range(0,16):
        sdk.set_parameter("base.lemo.mode", "in_h", i)
    for i in range(0,16):
        sdk.set_parameter("base.lemo.source", "high", i)

    sdk.set_parameter("base.t0.source", "lemo_0", 0)  
    
    sdk.execute_cmd("configure_base")
except:
    #print error mesagge and which function generate it
    print ("Errore durante la lettura dei parametri")
    failed = True
    
for sdk in sdks:
    try:
        sdk.set_parameter("dgtz.lemo.mode", "out", 0)
        sdk.set_parameter("dgtz.lemo.mode", "out", 1)
        sdk.set_parameter("dgtz.lemo.source", "t0_out", 0)
        sdk.set_parameter("dgtz.lemo.source", "t0_out", 1)
        sdk.set_parameter("trg.mode", "ext_trigger")

        sdk.execute_cmd("configure_dgtz")

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