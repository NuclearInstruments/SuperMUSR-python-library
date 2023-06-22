import adc120sdk
import json
from test_defs import *

print ("Questo test verifica la connessione del DAQ")

failed = False
sdks = []

test_report = []
i=0
for ip in DGZ_IP:
    sdks.append(adc120sdk.AdcControl())
    try:
        sdks[-1].connect(ip)
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
        print("SW-VER: " + swver + " (" + compile_data + ")  -- FPGA-VER: "  + hex(int(fwver))) 



        print(sdk.get_parameter("system.Tsys.rack",0))
        print(sdk.get_parameter("system.Tsys.dgtz",0))
        print(sdk.get_parameter("system.Tsys.dgtz",1))
        print(sdk.get_parameter("system.Tsys.dgtz",2))
        print(sdk.get_parameter("system.Tsys.dgtz",3))

    except:
        #print error mesagge and which function generate it
        print ("Errore durante la lettura dei parametri")
        failed = True

    i=i+1


# salva il report in json
with open('test_report.json', 'w') as outfile:
    json.dump(test_report, outfile)


if failed:
    print ("Test fallito")
    exit(-1)
else:
    print ("Test completato")