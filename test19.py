import adc120sdk
import json
import time
from test_defs import *
import numpy as np
import matplotlib.pyplot as plt

print ("Acquisizione segnale")

failed = False
sdks = []
daq = []

ip = DGZ_IP[###IP_INDEX###]

sdks.append(adc120sdk.AdcControl())
try:
    sdks[-1].connect(ip)
    print ("Digitizer %s connesso" % ip)
except:
    print ("Digitizer %s non raggiungibile" % ip)
    sdks.pop()
    failed = True
   
for sdk in sdks:

    s=int(float(sdk.get_parameter("dgtz.info.section")))

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
 
    W=sdk.read_data("get_waveforms")

    for j in range(0,###N_MEASURE###):
        W=sdk.read_data("get_waveforms")
        if W is not None:
            for ch in range(0,8):
                wave = W["wave"][ch]
                nwave = np.array(wave)
                # culate average, and averaged peak to peak
                avg = np.average(nwave)
                p2p = np.max(nwave) - np.min(nwave)
                rms = np.sqrt(np.mean(nwave **2))

                dt = 1.0
                rising_edges_a = np.where(np.diff(nwave) > 600)[0]  # Indici dei fronti di salita con tolleranza del 10%
                falling_edges_a = np.where(np.diff(nwave) < -750)[0]  # Indici dei fronti di discesa con tolleranza del 10%

                # Lista degli indici da mantenere
                if (len(rising_edges_a) !=0):
                    keep_edges = [rising_edges_a[0]]
                
                    # Controllo della distanza minima tra gli edge
                    for i in range(1, len(rising_edges_a)):
                        if rising_edges_a[i] - keep_edges[-1] > 50:
                            keep = True
                            for j in range(1, len(falling_edges_a)):
                                if (abs(rising_edges_a[i] - falling_edges_a[j]) < 50) :   
                                    keep = False
                            if (keep):
                                keep_edges.append(rising_edges_a[i])

                    # Nuova lista degli indici dei rising edge
                    rising_edges = np.array(keep_edges)

                    rise_times = np.zeros(len(rising_edges))  # Array per memorizzare i rise time
                    for i, edge in enumerate(rising_edges):
                        # Trova il tempo in cui il segnale sale dal 10% al 90% del suo valore massimo con tolleranza del 10%
                        threshold = 0.1 * (nwave[edge+10] - nwave[edge-10]) + nwave[edge-10]
                        idx_start = np.where(nwave[edge-10:edge+10] >= threshold)[0][0] + edge-10
                        threshold = 0.9 * (nwave[edge+10] - nwave[edge-10]) + nwave[edge-10]
                        idx_end = np.where(nwave[edge-10:edge+10] >= threshold)[0][0] + edge-10
                        rise_times[i] = (idx_end - idx_start) * dt  # Calcola il rise time
                
                    # Calcola il tempo medio di salita
                    rise_time = np.average(rise_times)
                    #calcolo il periodo dell'onda di ingresso dai rising edges
                    period = np.average(np.diff(rising_edges[2:]))
                    frequency = 1/period * 10e9
                    print ("DAQ "+ str(s))
                    print ("Channel %d" % ch)
                    print ("Average: %.2f" % avg)
                    print ("Peak to peak: %.2f" % p2p)
                    print ("RMS: %.2f" % rms)
                    print ("Frequency: %.2f" % frequency)
                    print ("Rise time: %.2f ns" % rise_time)

                    data = {
                            "daq" : s,
                            "channel" : ch,
                            "rms" : rms,
                            "mean" : avg,
                            "p2p" : p2p,
                            "freq" : frequency,
                            "rise" : rise_time
                    }    
    
                    daq.append(data)

                    test_wave = {
                        "wave" : wave[0:2047]
                    }

                    print("Wave" + str(ch+1) + "=" + json.dumps(test_wave, separators=(',', ':') ))
                else:
                    failed = True   

        # waveforms = W["wave"]

        # # Creazione della figura
        # fig, axs = plt.subplots(8, 1, figsize=(8, 16))

        # # Disegno delle forme d'onda
        # for ch in range(8):
        #     axs[ch].plot(waveforms[ch])
        #     axs[ch].set_title("Canale {}".format(ch))
        #     axs[ch].set_xlabel("Tempo")
        #     axs[ch].set_ylabel("Ampiezza")

        # # Mostra il grafico
        # plt.show()

test_report = {
    "daq" : daq
}

print("Report=" + json.dumps(test_report,  separators=(',', ':')))

if failed:
    print ("Test fallito")
    exit(-1)
else:
    print ("Test completato")
    exit(0)