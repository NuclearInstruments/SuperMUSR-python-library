import adc120sdk
import json
import time
from test_defs import *
import numpy as np

print ("Acquisizione segnale")

failed = False
sdk = adc120sdk.AdcControl()
test_report = []
i=0

sdks = []
i=0
for ip in DGZ_IP:
    sdks.append(adc120sdk.AdcControl())
    try:
        sdks[-1].connect(ip)
        print ("Digitizer %s connesso" % ip)
        test_report["dgtz"][i]["connection"] = True
    except:
        print ("Digitizer %s non raggiungibile" % ip)
        sdks.pop()
        failed = True
    
for sdk in sdks:
    try:
        s=sdk.get_parameter("dgtz.info.section")
        test_report["dgtz"][i]["section"] = int(float(s))

        sdk.set_parameter("dgtz.send_delay", "0")
        # digitizer configuration
        #set signal polarity to negative "pos" / "neg"
        sdk.set_parameter("in.polarity", "neg")
        # pre-trigger buffer len (us)
        sdk.set_parameter("dgtz.pre", 0.5)
        # post-trigger acquisition buffer (us)
        sdk.set_parameter("dgtz.post", 20)
        # delay on external trigger (us)
        sdk.set_parameter("dgtz.trg_delay", 0)
        # trigger source: "ext_trigger", "self_le", "self_de", "periodic", "manual", "lemo_0"
        sdk.set_parameter("trg.mode", "self_le")
        # internal trigger mode: "or", "and2", "and"
        sdk.set_parameter("trg.self_coinc", "or")
        # periodic trigger rate (Hz)
        sdk.set_parameter("trg.self_rate", 50)
        # trigger inibition (ns)
        sdk.set_parameter("trg.trigger_inib", 10)
        # parameter those are different for each channel of the digitizer
        for i in range(0, 8):
            # trigger threshold (LSB)
            sdk.set_parameter("trg.threshold", 2000, i)
            # trigger mask (LSB)
            sdk.set_parameter("trg.mask", 0, i)
            # digital input offset
            #sdk.set_parameter("in.offset", -1350, i)
            sdk.set_parameter("in.offset", 0, i)
            # trigger threshold (LSB)
            sdk.set_parameter("in.chmap", i, i)
        
        try:
            sdk.execute_cmd("configure_dgtz")
        except Exception as e:
            failed = True
            print("Error executing digitizer{i} programming:" + str(e))

        try:
            sdk.execute_cmd("start_acquisition")
        except Exception as e:
            failed = True
            print("Error executing digitizer{i} start:" + str(e))
   
        for j in range(0,100):
            W=sdk.read_data("get_waveforms")
            if W is not None:
                for ch in range(0,8):
                    wave = W["data"]["wave"][ch]
                    
                    # culate average, and averaged peak to peak
                    avg = np.average(wave)
                    p2p = np.max(wave) - np.min(wave)
                    rms = np.sqrt(np.mean(wave**2))

                    dt = 1.0
                    rising_edges = np.where(np.diff(wave) > 0.1)[0]  # Indici dei fronti di salita con tolleranza del 10%
                    rise_times = np.zeros(len(rising_edges))  # Array per memorizzare i rise time
                    for i, edge in enumerate(rising_edges):
                        # Trova il tempo in cui il segnale sale dal 10% al 90% del suo valore massimo con tolleranza del 10%
                        threshold = 0.1 * (wave[edge+1] - wave[edge]) + wave[edge]
                        idx_start = np.where(wave[edge:] >= threshold)[0][0] + edge
                        threshold = 0.9 * (wave[edge+1] - wave[edge]) + wave[edge]
                        idx_end = np.where(wave[edge:] >= threshold)[0][0] + edge
                        rise_times[i] = (idx_end - idx_start) * dt  # Calcola il rise time
                    
                    # Calcola il tempo medio di salita
                    rise_time = np.average(rise_times)

                    test_report["dgtz"][i]["rms"] = rms
                    test_report["dgtz"][i]["avg"] = avg
                    test_report["dgtz"][i]["p2p"] = p2p
                    test_report["dgtz"][i]["rise_times"] = rise_times
                    test_report["dgtz"][i]["rise_time"] = rise_time
                    test_report["dgtz"][i]["wave"] = wave

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