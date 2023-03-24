import adc120sdk
import json
import sys
from test_defs import *

print ("Questo test verifica la connessione del DAQ")

failed = False
sdks = []
daq=[]

for ip in DGZ_IP:
    sdks.append(adc120sdk.AdcControl())
    try:
        sdks[-1].connect(ip)
        print ("Digitizer %s connesso" % ip)
    except:
        print ("Digitizer %s non raggiungibile" % ip)
        sdks.pop()
        failed = True
   
for sdk in sdks:
    try:
        s=sdk.get_parameter("dgtz.info.section")
        section = int(float(s))
        sn = sdk.get_parameter("system.serialnumber")
        swver = sdk.get_parameter("system.swversion")
        compile_data = sdk.get_parameter("system.compile_data")
        fwver = sdk.get_parameter("dgtz.probes.fwver")

        print("sn: " + sn + "  section: " + str(section))
        print("SW-VER: " + swver + " (" + compile_data + ")  -- FPGA-VER: "  + fwver)

        d = {
            "connection" : True,
            "section" : section,
            "sn" : sn,
            "swver" : str(swver),
            "fwver" : str(fwver),
            "compile_data" : str(compile_data)}
        daq.append(d)

        base = {
            "Track" : sdk.get_parameter("system.Tsys.rack",0),
            "Tsys0" : sdk.get_parameter("system.Tsys.dgtz",0),
            "Tsys1" : sdk.get_parameter("system.Tsys.dgtz",1),
            "Tsys2" : sdk.get_parameter("system.Tsys.dgtz",2),
            "Tsys3" : sdk.get_parameter("system.Tsys.dgtz",3)
        }

    except:
        #print error mesagge and which function generate it
        print ("Errore durante la lettura dei parametri")
        failed = True

test_report = {
    "digitizer":daq,
    "temperature":base
}

print("Report=" + json.dumps(test_report,  separators=(',', ':')))

if failed:
    print ("Test fallito")
    exit(-1)
else:
    print ("Test completato")
    exit(0)
