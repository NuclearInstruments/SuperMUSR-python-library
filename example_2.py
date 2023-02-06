
import adc120sdk

CH_MAP = range(0,32)
DGZ_IP = ["tcp://192.168.102.167:5557"]

#DGZ_IP = ["tcp://d1.sw:10112"]

sdks = []

for ip in DGZ_IP:
    sdks.append(adc120sdk.AdcControl())
    sdks[-1].connect(ip)


#for each connected digitizer
for idx, sdk in enumerate(sdks):
    try:
        sdk.execute_cmd("stop_acquisition")
    except:
        print ("Digitized is not runnig")

    # get digitizer section
    s=sdk.get_parameter("dgtz.info.section")
    section = int(float(s))
    sn = sdk.get_parameter("system.serialnumber")
    swver = sdk.get_parameter("system.swversion")
    compile_data = sdk.get_parameter("system.compile_data")
    fwver = sdk.get_parameter("dgtz.probes.fwver")

    print("sn: " + sn + "  section: " + str(section))
    print("SW-VER: " + swver + " (" + compile_data + ")  -- FPGA-VER: "  + fwver)
    # the delay minimum between trigger and status packet redout
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
        sdk.set_parameter("in.chmap", CH_MAP[idx*8+i], i)



    # multi-photon processing
    # spectrum readout mode: "manual", "auto"
    sdk.set_parameter("mp.spectrum_readout_mode", "manual")
    # spectrum algorithm: "charge_integrator", "peak_holder"
    sdk.set_parameter("mp.spectrum_mode", "charge_integrator")
    # periodic spectrum send and reset
    sdk.set_parameter("mp.auto_spectrum_time", 5000)
    # acquisition gate length (ms)
    sdk.set_parameter("mp.gate_len", 30)
    # delay from trigger (ms)
    sdk.set_parameter("mp.delay_from_trigger", 0.5)
    # self trigger inibhit (us)
    sdk.set_parameter("mp.trigger_inib", 0)
    # baseline length (samples)
    sdk.set_parameter("mp.bl_len", 0.05)
    # baseline hold (us)
    sdk.set_parameter("mp.bl_hold", 0.05)
    # integration pre trigger
    sdk.set_parameter("mp.int_pre", 0.025)      #25u 0.015 #50u 0.025
    # integration post trigger
    sdk.set_parameter("mp.int_post", 0.100)     #25u 0.015 #50u 0.1
    # peak detector search window
    sdk.set_parameter("mp.peak_detector_window", 0.2)
    for i in range(0, 8):
        # enable multi-photon spectrum
        sdk.set_parameter("mp.enable", "true", i)
        # gain of charge integration
        sdk.set_parameter("mp.gain", 2, i)
        # single photon threshold
        sdk.set_parameter("mp.threshold", 15, i)

        sdk.set_parameter("mp.offset", 150, i)
    # offset of spectrum

    # configure io
    # configure digitizer lemo mode "in_h", "in_50", "out"
    sdk.set_parameter("dgtz.lemo.mode", "out", 0)
    sdk.set_parameter("dgtz.lemo.mode", "out", 1)

    # configure digitizer lemo output source
    # gnd", "high", "t0_out", "trigger_out", "tot_ch0",
    # "tot_ch1","tot_ch2","tot_ch3","tot_ch4","tot_ch5","tot_ch6","tot_ch7",
    # "run", "busy", "acquisition","mp_gate"
    sdk.set_parameter("dgtz.lemo.source", "t0_out", 0)
    sdk.set_parameter("dgtz.lemo.source", "trigger_out", 1)

    # configure digitizer sync_out output source
    # gnd", "high", "t0_out", "trigger_out", "tot_ch0",
    # "tot_ch1","tot_ch2","tot_ch3","tot_ch4","tot_ch5","tot_ch6","tot_ch7",
    # "run", "busy", "acquisition","mp_gate"
    for i in range(0,8):
        sdk.set_parameter("dgtz.sync.outmode", "tot_ch" + str(i), i)
    
    sdk.set_parameter("dgtz.sync.outmode", "trigger_out", 0)

    for i in range(0,8):
        sdk.set_parameter("dgtz.emu.amp", 100+100*i,i)
        sdk.set_parameter("dgtz.emu.period", 5000,i)
    sdk.set_parameter("dgtz.emu.noiseamp", 10)
    sdk.set_parameter("dgtz.emu.offset", 100)
    sdk.set_parameter("dgtz.emu.enable_pulse", "true")
    sdk.set_parameter("dgtz.emu.enable", "true")


    sdk.execute_cmd("configure_dgtz")
 
    sdk.execute_cmd("reset_darkcount_spectra")

    sdk.execute_cmd("start_acquisition")

   



