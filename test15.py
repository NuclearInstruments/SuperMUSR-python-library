import adc120sdk
import json
import time
from test_defs import *

print ("Verifica comunicazione con la stave 2 e 3 (DAQ C)")

failed = False
sdk = adc120sdk.AdcControl()
stave=[]
ip = DGZ_IP[2]
try:
    sdk.connect(ip)
    print ("Digitizer %s connesso" % ip)
    #test_report["dgtz"][i]["connection"] = True
except:
    print ("Digitizer %s non raggiungibile" % ip)
    exit(-2)

try:
    sdk.set_parameter("base.stave.power", "true", 0)
    sdk.execute_cmd("configure_base")
    print ("Attendere accensione stave")
    time.sleep(10)
    try:
        sdk.execute_cmd("configure_staves")
    except Exception as e:
        failed = True
        print("Error executing stave programming:" + str(e))

    time.sleep(1)
    for i in range (0,2):
        stave_ok = sdk.get_parameter("stave.probes.stave_ok",i)
        stave_sn = sdk.get_parameter("stave.probes.stave_sn",i)
        stave_configured = sdk.get_parameter("stave.probes.stave_configured",i)
        stave_uptime = sdk.get_parameter("stave.probes.stave_uptime",i)
        stave_fwver = sdk.get_parameter("stave.probes.stave_fwver",i)
        
        print(stave_ok)
        print(stave_sn)
        print(stave_configured)
        print(stave_uptime)
        print(stave_fwver)

        data = {
            "stave_ok" : stave_ok,
            "stave_sn" : stave_sn,
            "stave_configured" : stave_configured,
            "stave_uptime" : stave_uptime,
            "stave_fwver" : str(stave_fwver)         
        }
        
        stave.append(data)

    sdk.set_parameter("base.stave.power", "false", 0)
    sdk.execute_cmd("configure_base")

except:
    #print error mesagge and which function generate it
    print ("Errore durante la lettura dei parametri")
    failed = True
    
test_report = {
    "stave":stave,
}

print("Report=" + json.dumps(test_report,  separators=(',', ':')))

if failed:
    print ("Test fallito")
    exit(-1)
else:
    print ("Test completato")
    exit(0)