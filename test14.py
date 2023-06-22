import adc120sdk
import json
import time
from test_defs import *

print ("Verifica comunicazione con la stave 0 e 1 (DAQ A)")

failed = False
sdk = adc120sdk.AdcControl()
test_report = []
i=0
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
    time.sleep(2)
    sdk.set_parameter("base.stave.power", "true", 0)
    sdk.execute_cmd("configure_base")
    print ("Attendere accensione stave")
    time.sleep(15)
    try:
        for i in range (0,1000):
            sdk.execute_cmd("configure_staves")
    except Exception as e:
        failed = True
        print("Error executing stave programming:" + str(e))

    time.sleep(1)
    for i in range (0,2):
        print(sdk.get_parameter("stave.probes.stave_ok",i))
        print(sdk.get_parameter("stave.probes.stave_sn",i))
        print(sdk.get_parameter("stave.probes.stave_configured",i))
        print(sdk.get_parameter("stave.probes.stave_uptime",i))
        print(sdk.get_parameter("stave.probes.stave_fwver",i))

except:
    #print error mesagge and which function generate it
    print ("Errore durante la lettura dei parametri")
    failed = True
    
  
if failed:
    print ("Test fallito")
    exit(-1)
else:
    print ("Test completato")