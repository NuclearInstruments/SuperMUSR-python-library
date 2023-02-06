
import adc120sdk

CH_MAP = range(0,32)
DGZ_IP = ["tcp://192.168.102.186:5557"]

#DGZ_IP = ["tcp://d1.sw:10112"]

sdks = []

for ip in DGZ_IP:
    sdks.append(adc120sdk.AdcControl())
    sdks[-1].connect(ip)


#for each connected digitizer
for idx, sdk in enumerate(sdks):
    print("----- MODULE 1 -----")
    print("stave.probes.stave_uptime: ", float(sdk.get_parameter("stave.probes.stave_uptime")))
    print("stave.probes.stave_fwver: ", float(sdk.get_parameter("stave.probes.stave_fwver")))
    for i in range(0,8):
        print("stave.T.probes.Tsipm_" + str (i) + ": ", float(sdk.get_parameter("stave.T.probes.Tsipm",i)))
    for i in range(0,12):
        print("stave.BIAS.probes.correction_" + str (i) + ": ", float(sdk.get_parameter("stave.BIAS.probes.correction",i)))        

    hvok = int(sdk.get_parameter("stave.BIAS.probes.hvok",0))
    if (hvok):
        print("stave.BIAS.probes.fw: ", float(sdk.get_parameter("stave.BIAS.probes.fw",0)))
        print("stave.BIAS.probes.Imodule: ", float(sdk.get_parameter("stave.BIAS.probes.Imodule",0)))
        print("stave.BIAS.probes.Vmodule: ", float(sdk.get_parameter("stave.BIAS.probes.Vmodule",0)))
        print("stave.BIAS.probes.HVON: ", int(sdk.get_parameter("stave.BIAS.probes.HVON",0)))
        print("stave.BIAS.probes.protection: ", int(sdk.get_parameter("stave.BIAS.probes.protection",0)))
    else:
        print ("HV 1 FAULT")    

    print("----- MODULE 2 -----")
    hvok = int(sdk.get_parameter("stave.BIAS.probes.hvok",1))
    if (hvok):
        print("stave.BIAS.probes.fw: ", float(sdk.get_parameter("stave.BIAS.probes.fw",1)))
        print("stave.BIAS.probes.Imodule: ", float(sdk.get_parameter("stave.BIAS.probes.Imodule",1)))
        print("stave.BIAS.probes.Vmodule: ", float(sdk.get_parameter("stave.BIAS.probes.Vmodule",1)))
        print("stave.BIAS.probes.HVON: ", int(sdk.get_parameter("stave.BIAS.probes.HVON",1)))
        print("stave.BIAS.probes.protection: ", int(sdk.get_parameter("stave.BIAS.probes.protection",1)))    
    else:
        print ("HV 2 FAULT")            