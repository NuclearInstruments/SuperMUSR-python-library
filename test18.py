import adc120sdk
import json
import time
from test_defs import *
import numpy as np

print ("Acquisizione rumore")

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
    try:
        s=int(float(sdk.get_parameter("dgtz.info.section")))
        #digitizer[i]["section"] = int(float(s))

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
        sdk.set_parameter("trg.mode", "periodic")
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
        
        sdk.set_parameter("base.common_clock.source", "clk_int", 0)
        sdk.execute_cmd("configure_base")

        for j in range(0,###N_MEASURE###):
            W=sdk.read_data("get_waveforms")
            if W is not None:
                for ch in range(0,8):
                    wave = W["wave"][ch]
                    nwave = np.array(wave)
                    # calculate noise RMS, mean and peak-to-peak
                    mean = np.average(nwave)
                    nwave = nwave - mean
                    rms = np.sqrt(np.mean(np.square(nwave)))
                   
                    p2p = np.max(nwave) - np.min(nwave)
                    # calculate fft of the waveform
                    fft = np.fft.fft(nwave)
                    # calculate the power spectrum
                    ps = np.abs(fft)**2
                    # calculate the frequency
                    freq = np.fft.fftfreq(len(ps), 1/1000)
                    # calculate the power spectrum density
                    psd = ps/np.sum(ps)
   
                    # fine the first five peaks in fft and save them
                    peaks = np.argpartition(psd, -5)[-5:]
                    # save the results in the report

                    print ("DAQ " + str(s))
                    print ("Channel %d" % ch)
                    print ("Average: %.2f" % mean)
                    print ("Peak to peak: %.2f" % p2p)
                    print ("RMS: %.2f" % rms)

                    data = {
                            "daq" : s,
                            "channel" : ch,
                            "rms" : rms,
                            "mean" : mean,
                            "p2p" : p2p
                    }    
   
                    daq.append(data)

                    test_wave = {
                        "wave" : wave[0:2047]
                    }

                    print("Wave" + str(ch+1) + "=" + json.dumps(test_wave, separators=(',', ':') ))
    except:
        #print error mesagge and which function generate it
        print ("Errore durante la lettura dei parametri")
        failed = True

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