#how to enable packet transiever
#sudo devmem2 0xAF030004 w 1
#sudo devmem2 0xAF030008 w 2
#sudo devmem2 0xAF03000C w 3
#sudo devmem2 0xAF030010 w 4
#sudo devmem2 0xAF030014 w 5
#sudo devmem2 0xAF030018 w 6
#sudo devmem2 0xAF03001C w 8
#sudo devmem2 0xAF030020 w 265
#sudo devmem2 0xAF030024 w 22
#sudo devmem2 0xAF030000 w 2
#sudo devmem2 0xAF030038 w 100000
#sudo devmem2 0xAF010004 w 0x99
#must be done after initializing digitizer

#(0)  192.168.102.167
#(1)  192.168.102.168
#(2)  192.168.102.169
#(3)  192.168.102.171

import adc120sdk

CH_MAP = range(0,32)
DGZ_IP = ["tcp://192.168.102.150:5557"]

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



    # check if digitizer is a stave controller
    #if (section % 2) == 0:
    #    for i in range(0, 16):
    #        # configure PID and temperature heater
    #        sdk.set_parameter("stave.PID.P", 1, i)
    #        sdk.set_parameter("stave.PID.I", 0.01, i)
    #        sdk.set_parameter("stave.PID.D", 0, i)
    #        sdk.set_parameter("stave.T.target", 35, i)
    #        sdk.set_parameter("stave.T.enable", "true", i)
#
    #    # configure BIAS
    sdk.set_parameter("stave.BIAS.enable", "false",0)
    sdk.set_parameter("stave.BIAS.V", 59,0)
    sdk.set_parameter("stave.BIAS.max_v", 62,0)
    sdk.set_parameter("stave.BIAS.max_i", 3,0)

    sdk.set_parameter("stave.BIAS.enable", "false",1)
    sdk.set_parameter("stave.BIAS.V", 52,1)
    sdk.set_parameter("stave.BIAS.max_v", 58,1)
    sdk.set_parameter("stave.BIAS.max_i", 3,1)
# #
    #    # configure BIAS compensation
    for i in range(0, 24):
        # correction_mode "off", "auto", "manual"
        sdk.set_parameter("stave.BIAS.correction_mode", "manual",i)
        sdk.set_parameter("stave.BIAS.correction_manual", 0.2,i)
        # SiPM correction coefficient in V/°C
        sdk.set_parameter("stave.BIAS.correction_coeff", 0.035)
        # offset in V
        sdk.set_parameter("stave.offset", 0,i)

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
    sdk.set_parameter("dgtz.lemo.mode", "in_50", 0)
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
        sdk.set_parameter("dgtz.sync.outmode", "gnd", i)
    
    sdk.set_parameter("dgtz.sync.outmode", "trigger_out", 0)

    # configure base lemo mode "in", "out"
    for i in range(0,16):
        sdk.set_parameter("base.lemo.mode", "in", i)

    # configure base lemo source
    # "gnd", "high", "t0_out", "common_trigger", "clk_in", "busy", "status_packet_int", "veto_int",
    # "frame_sp_rx", "veto_usart_rx", "pulse_gen", "frame_usart_tx", "veto_usart_tx", "lvds_x"
    # "lvds_x+16", "rj45_lvds_0", "rj45_lvds_1", "rj45_lvds_2", "rj45_lvds_3", "adc_sync", "reg_x", "veto_x",
    # "sync_a_0","sync_a_1", "sync_a_2", "sync_a_3", "sync_a_4", "sync_a_5", "sync_a_6", "sync_a_7",
    # "sync_b_0","sync_b_1", "sync_b_2", "sync_b_3", "sync_b_4", "sync_b_5", "sync_b_6", "sync_b_7",
    # "sync_c_0","sync_c_1", "sync_c_2", "sync_c_3", "sync_c_4", "sync_c_5", "sync_c_6", "sync_c_7",
    # "sync_d_0","sync_d_1", "sync_d_2", "sync_d_3", "sync_d_4", "sync_d_5", "sync_d_6", "sync_d_7"

    for i in range(0,16):
        sdk.set_parameter("base.lemo.source", "gnd", i)


    # configure base sync source
    # "gnd", "high", "common_trigger", "t0_out", "common_trigger", "clk_in", "busy", "status_packet_int",
    # "veto_int", "veto_in", "veto_in+8",
    # "lemo_0", "lemo_1", "lemo_2", "lemo_3", "lemo_4", "lemo_5", "lemo_6", "lemo_7",
    # "lemo_8", "lemo_9", "lemo_10", "lemo_11", "lemo_12", "lemo_13", "lemo_14", "lemo_15"
    for i in range(0,8):
        sdk.set_parameter("base.sync.outmode", "gnd", i)


    sdk.set_parameter("base.pulsegen.freq", 100000.0, 0)

    # configure status packet frame source uart
    # "lemo_0", "lemo_4", "lemo_8", "lemo_12", "rj45_lvds_0", "lvds_0", "lvds_8", "lvds_16", "lvds_24"
    # "frame_usart_tx"
    sdk.set_parameter("base.sp_rx.frame_source", "frame_usart_tx", 0)

    # configure status packet veto source uart
    # "lemo_1", "lemo_5", "lemo_9", "lemo_13", "rj45_lvds_1", "lvds_1", "lvds_9", "lvds_17", "lvds_25"
    # "veto_usart_tx"
    sdk.set_parameter("base.sp_rx.veto_source", "veto_usart_tx", 0)

    # configure T0 source
    # "gnd", "high", "t0_self", "rj45_lvds_0", "rj45_lvds_1", "rj45_lvds_2", "rj45_lvds_3",
    # "lvds_0", "lvds_1", "lvds_2", "lvds_3", "lvds_28", "lvds_29", "lvds_30", "lvds_31",
    # "lemo_0", "lemo_1", "lemo_2", "lemo_3", "lemo_4", "lemo_5", "lemo_6", "lemo_7",
    # "lemo_8", "lemo_9", "lemo_10", "lemo_11", "lemo_12", "lemo_13", "lemo_14", "lemo_15"
    sdk.set_parameter("base.t0.source", "lemo_0", 0)    

    sdk.set_parameter("base.t0.freq", 25.0, 0)

    # configure common_clk source
    # "clk_int", "clk_ext", "rj45_lvds_0", "rj45_lvds_1", "rj45_lvds_2", "rj45_lvds_3",
    # "lvds_16", "lvds_26"
    sdk.set_parameter("base.common_clock.source", "clk_int", 0)


    # configure adc_sync source
    # "internal", "gnd", "high", "rj45_lvds_0", "rj45_lvds_1", "rj45_lvds_2", "rj45_lvds_3",
    # "lvds_6", "lvds_14", "lvds_23", "lvds_27",
    # "lemo_0", "lemo_1", "lemo_2", "lemo_3", "lemo_4", "lemo_5", "lemo_6", "lemo_7",
    # "lemo_8", "lemo_9", "lemo_10", "lemo_11", "lemo_12", "lemo_13", "lemo_14", "lemo_15"

    sdk.set_parameter("base.adc_sync.source", "internal", 0)



    # configure emulator
    # trigger inibition (ns)
    for i in range(0,8):
        sdk.set_parameter("dgtz.emu.amp", 100+100*i,i)
        sdk.set_parameter("dgtz.emu.period", 5000,i)
    sdk.set_parameter("dgtz.emu.noiseamp", 0)
    sdk.set_parameter("dgtz.emu.offset", 0)
    sdk.set_parameter("dgtz.emu.enable_pulse", "false")
    sdk.set_parameter("dgtz.emu.enable", "false")


    # test parameter readback
    for i in range(0, 16):
        print(sdk.get_parameter("base.lemo.mode"),i)
        print(sdk.get_parameter("base.lemo.source"),i)

    for i in range(0, 8):
        print(sdk.get_parameter("base.sync.outmode"),i)

    print(float(sdk.get_parameter("mp.gain")))


    # configure event processor (fixed threshold)
    sdk.set_parameter("sw_process.enable", "false")
    sdk.set_parameter("sw_process.threshold", 520, 0)
    sdk.set_parameter("sw_process.threshold", 500, 1)
    sdk.set_parameter("sw_process.threshold", 520, 2)
    sdk.set_parameter("sw_process.threshold", 460, 3)
    sdk.set_parameter("sw_process.threshold", 3000, 4)
    sdk.set_parameter("sw_process.threshold", 3000, 5)
    sdk.set_parameter("sw_process.threshold", 3000, 6)
    sdk.set_parameter("sw_process.threshold", 3000, 7)
    sdk.set_parameter("sw_process.hist", 10)
    sdk.set_parameter("base.stave.power", "true", 0)
    
    
    # configure event processor (derivative threshold)
    # sdk.set_parameter("sw_process.enable", "true")
    # sdk.set_parameter("sw_process.threshold", 10, 0)
    # sdk.set_parameter("sw_process.threshold", 10, 1)
    # sdk.set_parameter("sw_process.threshold", 10, 2)
    # sdk.set_parameter("sw_process.threshold", 10, 3)
    # sdk.set_parameter("sw_process.threshold", 3000, 4)
    # sdk.set_parameter("sw_process.threshold", 3000, 5)
    # sdk.set_parameter("sw_process.threshold", 3000, 6)
    # sdk.set_parameter("sw_process.threshold", 3000, 7)
    # sdk.set_parameter("sw_process.hist", 25)    

    sdk.execute_cmd("configure_dgtz")
    #sdk.execute_cmd("configure_base")
    

    try:
        sdk.execute_cmd("configure_hv")
    except Exception as e:
        print("Error executing HV programming:" + str(e))
    

    try:
        sdk.execute_cmd("configure_staves")
    except Exception as e:
        print("Error executing stave programming:" + str(e))

    sdk.execute_cmd("reset_darkcount_spectra")

    # sdk.execute_cmd("manual_trigger")

    
    # print(sdk.read_data("get_darkcount_spectra"))
    # print(sdk.read_data("get_waveforms"))
    sdk.execute_cmd("start_acquisition")

    print(sdk.get_parameter("system.Tsys.rack",0))
    print(sdk.get_parameter("system.Tsys.dgtz",0))
    print(sdk.get_parameter("system.Tsys.dgtz",1))
    print(sdk.get_parameter("system.Tsys.dgtz",2))
    print(sdk.get_parameter("system.Tsys.dgtz",3))
    print(sdk.get_parameter("system.availableram",0))
    print(sdk.get_parameter("system.ipaddress",0))
   



