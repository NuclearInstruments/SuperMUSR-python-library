import adc120sdk
import json
from test_defs import *

print ("Verifica distribuzione del T0")
print ("Applicare T0 sul lemo 0 della base e verificare con un oscilloscopio che il T0")
print ("Appaia sul lemo 0 e 1 di tutte le DAQ")
failed = False
sdk = adc120sdk.AdcControl()
test_report = []
i=0
ip = DGZ_IP[0]
try:
    sdk.connect(ip)
    print ("Digitizer %s connesso" % ip)
    test_report["dgtz"][i]["connection"] = True
except:
    print ("Digitizer %s non raggiungibile" % ip)
    exit(-2)


try:
    sdk.set_parameter("base.common_clock.source", "clk_in", 0)
  
    for i in range(0,16):
        sdk.set_parameter("base.lemo.mode", "in", i)
    for i in range(0,16):
        sdk.set_parameter("base.lemo.source", "high", i)

    sdk.set_parameter("base.t0.source", "lemo_0", 0)  
    
    sdk.set_parameter("dgtz.lemo.mode", "out", 0)
    sdk.set_parameter("dgtz.lemo.mode", "out", 1)
    sdk.set_parameter("dgtz.lemo.source", "t0_out", 0)
    sdk.set_parameter("dgtz.lemo.source", "trigger_out", 1)

    sdk.set_parameter("trg.mode", "ext_trigger")

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