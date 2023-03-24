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
  
    sdk.set_parameter("stave.BIAS.enable", "true",0)
    sdk.set_parameter("stave.BIAS.V", 47,0)
    sdk.set_parameter("stave.BIAS.max_v", 62,0)
    sdk.set_parameter("stave.BIAS.max_i", 3,0)

    sdk.set_parameter("stave.BIAS.enable", "true",1)
    sdk.set_parameter("stave.BIAS.V", 56,1)
    sdk.set_parameter("stave.BIAS.max_v", 62,1)
    sdk.set_parameter("stave.BIAS.max_i", 3,1)

    try:
        sdk.execute_cmd("configure_hv")
    except Exception as e:
        failed = True
        print("Error executing hv programming:" + str(e))

    for i in range (0,25):
        Vmodule0 = sdk.get_parameter("stave.BIAS.probes.Vmodule",0)
        Vmodule1 = sdk.get_parameter("stave.BIAS.probes.Vmodule",1)
        Imodule0 = sdk.get_parameter("stave.BIAS.probes.Imodule",0)
        Imodule1 = sdk.get_parameter("stave.BIAS.probes.Imodule",1)
        
        print(Vmodule0) 
        print(Vmodule1) 
        print(Imodule0) 
        print(Imodule1)

        data = {
               "hv_0_V" :  Vmodule0,
               "hv_1_V" :  Vmodule1,
               "hv_0_I" :  Imodule0,
               "hv_1_I" :  Imodule1
        } 

        hv.append(data)        
        time.sleep(0.5)
    # sdk.set_parameter("stave.BIAS.enable", "false",0)
    # sdk.set_parameter("stave.BIAS.enable", "false",1)
    sdk.execute_cmd("configure_hv") 

except:
    #print error mesagge and which function generate it
    print ("Errore durante la lettura dei parametri")
    failed = True
 
test_report = {
    "hv":hv,
}

print("Report=" + json.dumps(test_report,  separators=(',', ':')))

if failed:
    print ("Test fallito")
    exit(-1)
else:
    print ("Test completato")
    exit(0)