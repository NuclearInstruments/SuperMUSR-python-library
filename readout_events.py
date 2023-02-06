
import adc120sdk
import threading
import time
from DigitizerEventListMessage import DigitizerEventListMessage


DGZ_IP = ["tcp://192.168.102.186:5555"]
#DGZ_IP = ["tcp://d1.sw:10113"]

sdks = []


def thread_readout_function(sdk):
    while 1:
        message = sdk.get_events()
        fb = DigitizerEventListMessage.GetRootAsDigitizerEventListMessage(message)
        print("----------")
        c = fb.ChannelAsNumpy()
        t = fb.TimeAsNumpy()
        v = fb.VoltageAsNumpy()
        for i in range(0,fb.ChannelLength()):
            print(str(c[i]) + "  -->  " + str(t[i]) + "    " + str(v[i]))
    


for ip in DGZ_IP:
    sdks.append(adc120sdk.AdcControl())
    sdks[-1].connect_events(ip)

for idx, sdk in enumerate(sdks):
    threading.Thread(target=thread_readout_function, args=(sdk,)).start()

while 1:
    time.sleep(1)