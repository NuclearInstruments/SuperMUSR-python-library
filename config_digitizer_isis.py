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

import numpy as np

 

CH_MAP = range(0,32)

#'''

#New Digitiser IP adress assignement, as of 23 May 2023.

#DAQ 1 = 130.246.55.20

##DAQ 2 = 130.246.55.50

#DAQ 3 = 130.246.55.14

#DAQ 4 = 130.246.55.66

#'''

 

 

#DGZ_IP = ["tcp://130.246.50.78:5557"]

DGZ_IP = ["tcp://130.246.54.157:5557"]

 

 

sdks = []

 

for ip in DGZ_IP:

    sdks.append(adc120sdk.AdcControl())

    sdks[-1].connect(ip)

 

#for each connected digitizer

for idx, sdk in enumerate(sdks):

    try:

        sdk.execute_cmd("stop_acquisition") #always stop before changing anthing!

    except:

        print ("Digitized is not running")

       

    #sdk.set_parameter("dgtz.info.section", DGZ_ID_Section[idx])

 

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

    sdk.set_parameter("dgtz.send_delay", "0") #delay 'waiting /listing' for status and vetos, then sent to kafka.

    # digitizer configuration

    #set signal polarity to negative "pos" / "neg"

    sdk.set_parameter("in.polarity", "neg") #Always positive plotted. This is inversion  on / off. neg for stave, pos for fake data!

    # pre-trigger buffer len (us)

    sdk.set_parameter("dgtz.pre", 0.5)    #sdk.set_parameter("dgtz.pre", 0.001) # as short as it can go

    # post-trigger acquisition buffer (us). The aquisition length.

    sdk.set_parameter("dgtz.post", 16.) #30

    #sdk.set_parameter("dgtz.post", 0.001) #as shot as it can go

    # delay on external trigger (us)

    sdk.set_parameter("dgtz.trg_delay", 0)

    # trigger source: "ext_trigger", "self_le", "self_de", "periodic", "manual", "lemo_0"

    sdk.set_parameter("trg.mode", "ext_trigger") # self_le is the LE trigger level

    #sdk.set_parameter("trg.mode", "self_le") 

    #sdk.set_parameter("trg.mode", "periodic") 

    # internal trigger mode: "or", "and2", "and"

    sdk.set_parameter("trg.self_coinc", "or") # "or" is or,  "and2" is 2 fold coincidence. "and" is a coincidence for all 8.

    # periodic trigger rate (Hz) (use to see the baseline)

    sdk.set_parameter("trg.self_rate", 5) # the periodic trigger rate (Hz). 50 is a trigger every 20ms for example.

    # trigger inibition (ns). Only useful for slow signals, to avoid multiple-triggering.

    sdk.set_parameter("trg.trigger_inib", 10)

 

    # parameter those are different for each channel of the digitizer

   

    #my_thresholds = [3000,3000,3000,3000,3000,3000,3000,3000]

    my_thresholds = [1200,1200,1800,1600,1400,1400,1400,1400] #thresholds for DAQ1

    #my_thresholds = [1200, 1400, 1200, 1300, 800, 800, 800, 800] #thresholds for DAQ

    my_thresholds = [600, 560, 760, 830, 690, 970, 740, 680]

    #my_thresholds = my_thresholds * 2

    #my_mask = [1,1,1,1,1,1,1,1] # All off

    #my_mask = [0,0,0,0,0,0,0,0] # All on

    my_mask = [1,1,1,0,1,1,1,1] # All off

    my_offsets = [-340,-340,-340,-340,-1500,-1500,-1500,-1500] #offsets for DAQ3 for 1st stave

    #my_offsets = [-1480,-1250,-1230,-1300,-1190,-1240,-1210,-1250] #for 2nd stave at DAQ 1

  

    

    for i in range(0, 8):

        # trigger threshold (LSB)

        sdk.set_parameter("trg.threshold", 2500, i)  #2000 my_thresholds[i]

        # trigger mask (LSB)

        sdk.set_parameter("trg.mask", my_mask[i], i) # set to 1 to disable triggering of the channel

        # digital input offset

        #sdk.set_parameter("in.offset", -1350, i). Digital only, not actually shifting the bit depth.

        sdk.set_parameter("in.offset",0, i)  # -340 for "new" stave

        #sdk.set_parameter("in.offset",-1340, i)   # -1500 for "old" stave

 

        # trigger threshold (LSB)

        sdk.set_parameter("in.chmap", CH_MAP[idx*8+i], i) #to reasign ch number to Kafka. A0-8, B0-8, C0-8, D0-8 to #32

  

#

    #    # configure BIAS

    # last argument is the HV channel (0,1) and nothing more. There are two HV chans on the DAQ.

    #DAQ 0 (A) controls HV 1,2.

    #DAQ 1 (B) - nothing

    #DAQ 2 (C) - controls HV 3,4.

    #DAQ 3 (D) - nopthing

    myBias = 57

    sdk.set_parameter("stave.BIAS.enable", "true",0) # True/False for Bias on/off

    sdk.set_parameter("stave.BIAS.V", myBias,0)

    sdk.set_parameter("stave.BIAS.max_v", 61,0) #safety limit

    sdk.set_parameter("stave.BIAS.max_i", 3,0) #Kill if over this

 

    sdk.set_parameter("stave.BIAS.enable", "true",1) # I changed this to true

    sdk.set_parameter("stave.BIAS.V", myBias,1)

    sdk.set_parameter("stave.BIAS.max_v", 61,1)

    sdk.set_parameter("stave.BIAS.max_i", 3,1)

# #

 

# check if digitizer is a stave controller

#if (section % 2) == 0:

    

    heater_temp = 35

    # 2 PID values per channel i.e. the first two values belong to channel 0 etc.

    my_PIDvalues_P = [25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25]

    my_PIDvalues_I = [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5]

    my_PIDvalues_D = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

   

    for i in range(0, 16):

#        # configure PID and temperature heater

         sdk.set_parameter("stave.PID.P", my_PIDvalues_P[i], i)     #P default value pid_P = 25

         sdk.set_parameter("stave.PID.I", my_PIDvalues_I[i], i)     #I default value pid_I = 5

         sdk.set_parameter("stave.PID.D", my_PIDvalues_D[i], i)     #D defalut value pid_D = 0

         sdk.set_parameter("stave.T.target", heater_temp, i)

         sdk.set_parameter("stave.T.enable", "false", i)

 

    #    # configure BIAS compensation

    for i in range(0, 24): #upto 12 chans per stave = 24 total.

        # correction_mode "off", "auto", "manual"

        # bias is always the same to the stave, but each chan is changed (+ or -) by the amount upto 2V.

        sdk.set_parameter("stave.BIAS.correction_mode", "manual",i) # in software manually change voltage by

        sdk.set_parameter("stave.BIAS.correction_manual", 0,i) # if in manual, the second argument is the correction offset

        # SiPM correction coefficient in V/°C

        sdk.set_parameter("stave.BIAS.correction_coeff", 0.035) # this is for auto as per a coefficent (linear)

        # offset in V

        sdk.set_parameter("stave.offset", -0.6,i) #this is DC offset, tune to scale dV over the ADC bit depth. TODO.

       

    

 

    # multi-photon processing

    # spectrum readout mode: "manual", "auto"

    sdk.set_parameter("mp.spectrum_readout_mode", "auto")

    # spectrum algorithm: "charge_integrator", "peak_holder"

    sdk.set_parameter("mp.spectrum_mode", "charge_integrator")

    # periodic spectrum send and reset

    sdk.set_parameter("mp.auto_spectrum_time", 5000)

    # acquisition gate length (ms)

    sdk.set_parameter("mp.gate_len", 20)

    # delay from trigger (ms)

    sdk.set_parameter("mp.delay_from_trigger", 0.5)

    # self trigger inibhit (us)

    sdk.set_parameter("mp.trigger_inib", 0)

    # baseline length (samples)

    sdk.set_parameter("mp.bl_len", 0.05)

    # baseline hold (us)

    sdk.set_parameter("mp.bl_hold", 0.05)

    # integration pre trigger

    sdk.set_parameter("mp.int_pre", 0.015)      #25u 0.015 #50u 0.025

    # integration post trigger

    sdk.set_parameter("mp.int_post", 0.015)     #25u 0.015 #50u 0.1

    # peak detector search window

    sdk.set_parameter("mp.peak_detector_window", 0.5)

   

    

    #my_mp_gain = [9,9,9,9,9,9,9,9]

    #my_mp_threshold = [20,20,20,20,20,20,20,20]

    #my_mp_offset = [600,600,600,600,600,600,600,600]

    for i in range(0, 8):

        # enable multi-photon spectrum

        sdk.set_parameter("mp.enable", "true", i)

        # gain of charge integration

        sdk.set_parameter("mp.gain", 2, i)

        # single photon threshold

        sdk.set_parameter("mp.threshold", 15, i)

        # offset of spectrum

        sdk.set_parameter("mp.offset", 150, i)

       

    

    

 

    # configure io

    # configure digitizer lemo mode "in_h", "in_50", "out"

    sdk.set_parameter("dgtz.lemo.mode", "in_50", 0) #High or 50Ohm termination selectable, 0 is the index (left)

    sdk.set_parameter("dgtz.lemo.mode", "out", 1) #High or 50Ohm termination selectable, 0 is the index (left)

 

    # configure digitizer lemo output source

    # gnd", "high", "t0_out", "trigger_out", "tot_ch0",

    # "tot_ch1","tot_ch2","tot_ch3","tot_ch4","tot_ch5","tot_ch6","tot_ch7",

    # "run", "busy", "acquisition","mp_gate" 

    # all diagnostics to use. High when running, transfering, aquiring or gating.

    sdk.set_parameter("dgtz.lemo.source", "t0_out", 0) # (Lemo 17, on the digitiser)

    sdk.set_parameter("dgtz.lemo.source", "trigger_out", 1)

   

    

 

    # configure digitizer sync_out output source

    # gnd", "high", "t0_out", "trigger_out", "tot_ch0",

    # "tot_ch1","tot_ch2","tot_ch3","tot_ch4","tot_ch5","tot_ch6","tot_ch7",

    # "run", "busy", "acquisition","mp_gate"

    #Each Digitiser has eight sync lines. Can choose where each one goes.

    #For example 8 x 4 can go to SAMTEC connector.

    # must configure the syn/routing matrix.

    # NOTe to Dan - See andrea's example email for all ToT to Syn to SAMTEC

    for i in range(0,8):

        sdk.set_parameter("dgtz.sync.outmode", "gnd", i)

   

    sdk.set_parameter("dgtz.sync.outmode", "trigger_out", 0)

 

    # configure base lemo mode "in", "out"

    # lemo's on base are always 50Ohm, unless changing jumper inside.

    for i in range(0,16):

        sdk.set_parameter("base.lemo.mode", "in_h", i)

 

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

        #print("base.lemo.source  = ", i, " = " , sdk.get_parameter("base.lemo.source"))

       

 

 

    # configure base sync source

    # "gnd", "high", "common_trigger", "t0_out", "common_trigger", "clk_in", "busy", "status_packet_int",

    # "veto_int", "veto_in", "veto_in+8",

    # "lemo_0", "lemo_1", "lemo_2", "lemo_3", "lemo_4", "lemo_5", "lemo_6", "lemo_7",

    # "lemo_8", "lemo_9", "lemo_10", "lemo_11", "lemo_12", "lemo_13", "lemo_14", "lemo_15"

    for i in range(0,8):

        sdk.set_parameter("base.sync.outmode", "gnd", 0)

       

 

 

sdk.set_parameter("base.pulsegen.freq", 100000.0, 0)



# configure status packet frame source uart

# "lemo_0", "lemo_4", "lemo_8", "lemo_12", "rj45_lvds_0", "lvds_0", "lvds_8", "lvds_16", "lvds_24"

# "frame_usart_tx"

sdk.set_parameter("base.sp_rx.frame_source", "lemo_0", 0)

#sdk.set_parameter("base.sp_rx.frame_source", "frame_usart_tx", 0)



# configure status packet veto source uart

# "lemo_1", "lemo_5", "lemo_9", "lemo_13", "rj45_lvds_1", "lvds_1", "lvds_9", "lvds_17", "lvds_25"

# "veto_usart_tx"

sdk.set_parameter("base.sp_rx.veto_source", "lemo_1", 0)  #  this is lemo 2 on the front panel

#sdk.set_parameter("base.sp_rx.veto_source", "veto_usart_tx", 0)





# configure T0 source

# "gnd", "high", "t0_self", "rj45_lvds_0", "rj45_lvds_1", "rj45_lvds_2", "rj45_lvds_3",

# "lvds_0", "lvds_1", "lvds_2", "lvds_3", "lvds_28", "lvds_29", "lvds_30", "lvds_31",

# "lemo_0", "lemo_1", "lemo_2", "lemo_3", "lemo_4", "lemo_5", "lemo_6", "lemo_7",

# "lemo_8", "lemo_9", "lemo_10", "lemo_11", "lemo_12", "lemo_13", "lemo_14", "lemo_15"

sdk.set_parameter("base.t0.source", "lemo_2", 0)    # the third lemo on the front panel

print("-----")

print("base.t0.source  =  " , sdk.get_parameter("base.t0.source"))

print("-----")

#sdk.set_parameter("base.t0.source", "t0_self", 0)   



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

    sdk.set_parameter("dgtz.emu.amp", 1000+100*i,i)

    sdk.set_parameter("dgtz.emu.period", 500,i)

sdk.set_parameter("dgtz.emu.noiseamp", 1000)

sdk.set_parameter("dgtz.emu.offset", 2000)



sdk.set_parameter("dgtz.emu.enable_pulse", "false") #data is coming from stave

sdk.set_parameter("dgtz.emu.enable", "false") #data is coming from stave



#sdk.set_parameter("dgtz.emu.enable_pulse", "true") #fake data from generator

#sdk.set_parameter("dgtz.emu.enable", "true") #fake data from generator





# test parameter readbackfor the GPIO Lemo

for i in range(0, 16):

    print("base.lemo.mode    = ", i, " = " , sdk.get_parameter("base.lemo.mode"))

    print("base.lemo.source  = ", i, " = " , sdk.get_parameter("base.lemo.source"))

    

print("base.t0.source  =  " , sdk.get_parameter("base.t0.source"))

print("base.sp_rx.veto_source  =  " , sdk.get_parameter("base.sp_rx.veto_source"))

print("base.sp_rx.frame_source  =  " , sdk.get_parameter("base.sp_rx.frame_source"))

print(" trg.mode  =  " , sdk.get_parameter("trg.mode"))









for i in range(0, 8):

    print("base.sync.outmode   =  ", sdk.get_parameter("base.sync.outmode"),i)

    



print("mp.gain   = ", float(sdk.get_parameter("mp.gain")))

print("stave.BIAS.V", sdk.get_parameter("stave.BIAS.V",0))





# configure event processor (fixed threshold)

    



sdk.set_parameter("sw_process.enable", "true")

sdk.set_parameter("sw_process.histogram.trigger_mode",0)
sdk.set_parameter("sw_process.histogram.histeresys",5)

# sdk.set_parameter("sw_process.histogram.treshold", 20)
sdk.set_parameter("sw_process.histogram.treshold", 10,0)
sdk.set_parameter("sw_process.histogram.treshold", 10,1)
sdk.set_parameter("sw_process.histogram.treshold", 10,2)
sdk.set_parameter("sw_process.histogram.treshold", 20,3)
sdk.set_parameter("sw_process.histogram.treshold", 10,4)
sdk.set_parameter("sw_process.histogram.treshold", 10,5)
sdk.set_parameter("sw_process.histogram.treshold", 10,6)
sdk.set_parameter("sw_process.histogram.treshold", 10,7)


sdk.set_parameter("sw_process.histogram.treshold_ampl", 10,0)
sdk.set_parameter("sw_process.histogram.treshold_ampl", 10,1)
sdk.set_parameter("sw_process.histogram.treshold_ampl", 10,2)
sdk.set_parameter("sw_process.histogram.treshold_ampl", 10,3)
sdk.set_parameter("sw_process.histogram.treshold_ampl", 10,4)
sdk.set_parameter("sw_process.histogram.treshold_ampl", 10,5)
sdk.set_parameter("sw_process.histogram.treshold_ampl", 10,6)
sdk.set_parameter("sw_process.histogram.treshold_ampl", 10,7)

# for i in range(0,8):
#     sdk.set_parameter("sw_process.histogram.deconv_m", -0.925,i)

sdk.set_parameter("sw_process.histogram.deconv_enable", 0)

sdk.set_parameter("sw_process.histogram.delta", 10)

sdk.set_parameter("sw_process.histogram.inib", 10)

sdk.set_parameter("sw_process.histogram.rebin",4)

sdk.set_parameter("sw_process.histogram.nf",0)

sdk.set_parameter("sw_process.histogram.A.blsub",0)
sdk.set_parameter("sw_process.histogram.A.prebl",20)
sdk.set_parameter("sw_process.histogram.A.maxw",40)



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

sdk.execute_cmd("configure_base")





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



        

#print(sdk.read_data("get_waveforms")) #Needs to already be aquiring data. Returns  8 waveforms returned

sdk.execute_cmd("start_acquisition")

print("get_last_status_packet  = ", sdk.read_data("get_last_status_packet"))



    

    

    

       

    

    

# dan notes:

#sdks[0].execute_cmd("stop_acquisition") # if outside of enumerate loop index the sdk in the list