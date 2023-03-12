import adc120sdk
import json
import time
from test_defs import *

print ("Verifica comunicazione con la stave 2 e 3 (DAQ C)")

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
    sdk.set_parameter("base.stave.power", "true", 0)
    print ("Attendere accensione stave")
    time.sleep(10)
    try:
        sdk.execute_cmd("configure_staves")
    except Exception as e:
        failed = True
        print("Error executing stave programming:" + str(e))

    time.sleep(1)
    for i in range (0,2):
        test_report["HV"][i]["ok"] = sdk.get_parameter("stave.probes.stave_ok",0)
        test_report["HV"][i]["sn"] = sdk.get_parameter("stave.probes.stave_sn",0)
        test_report["HV"][i]["configured"] = sdk.get_parameter("stave.probes.stave_configured",0)
        test_report["HV"][i]["uptime"] = sdk.get_parameter("stave.probes.stave_uptime",0)
        test_report["HV"][i]["fwver"] = sdk.get_parameter("stave.probes.stave_fwver",0)

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