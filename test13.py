import adc120sdk
import json
import time
from test_defs import *

print ("Verifica distribuzione dell'HV dei moduli 2 e 3 (DAQ A)")
print ("Verificare con un multimetro la presenza di 47V su HV 2 e 56V su HV 3")

failed = False
sdk = adc120sdk.AdcControl()
test_report = []
i=0
ip = DGZ_IP[2]
try:
    sdk.connect(ip)
    print ("Digitizer %s connesso" % ip)
    test_report["dgtz"][i]["connection"] = True
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
        test_report["HV"][0]["V"] = sdk.get_parameter("stave.BIAS.probes.Vmodule",0)
        test_report["HV"][1]["V"] = sdk.get_parameter("stave.BIAS.probes.Vmodule",1)
        test_report["HV"][0]["I"] = sdk.get_parameter("stave.BIAS.probes.Imodule",0)
        test_report["HV"][1]["I"] = sdk.get_parameter("stave.BIAS.probes.Imodule",1)
        time.sleep(0.5)
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