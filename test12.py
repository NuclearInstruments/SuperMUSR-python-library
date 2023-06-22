import adc120sdk
import json
import time
from test_defs import *

print ("Verifica distribuzione dell'HV dei moduli 0 e 1 (DAQ A)")
print ("Verificare con un multimetro la presenza di 45V su HV 0 e 59V su HV 1")

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
  
    sdk.set_parameter("stave.BIAS.enable", "true",0)
    sdk.set_parameter("stave.BIAS.V", 45,0)
    sdk.set_parameter("stave.BIAS.max_v", 62,0)
    sdk.set_parameter("stave.BIAS.max_i", 3,0)

    sdk.set_parameter("stave.BIAS.enable", "true",1)
    sdk.set_parameter("stave.BIAS.V", 59,1)
    sdk.set_parameter("stave.BIAS.max_v", 62,1)
    sdk.set_parameter("stave.BIAS.max_i", 3,1)

    try:
        sdk.execute_cmd("configure_hv")
    except Exception as e:
        failed = True
        print("Error executing hv programming:" + str(e))

    for i in range (0,25):
        print(sdk.get_parameter("stave.BIAS.probes.Vmodule",0))
        print(sdk.get_parameter("stave.BIAS.probes.Vmodule",1))
        print(sdk.get_parameter("stave.BIAS.probes.Imodule",0))
        print(sdk.get_parameter("stave.BIAS.probes.Imodule",1))
        time.sleep(0.5)
    
except:
    #print error mesagge and which function generate it
    print ("Errore durante la lettura dei parametri")
    failed = True
    
  

if failed:
    print ("Test fallito")
    exit(-1)
else:
    print ("Test completato")