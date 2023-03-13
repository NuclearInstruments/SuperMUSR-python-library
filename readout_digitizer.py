
import adc120sdk
import threading
import time
from DigitizerAnalogTraceMessage import DigitizerAnalogTraceMessage


DGZ_IP = ["tcp://192.168.102.150:5556"]
#DGZ_IP = ["tcp://d1.sw:10113"]

sdks = []


def thread_readout_function(sdk):
    while 1:
        message = sdk.get_data()
        fb = DigitizerAnalogTraceMessage.GetRootAsDigitizerAnalogTraceMessage(message)
        for i in range(0, fb.ChannelsLength()):
            data = fb.Channels(i).VoltageAsNumpy()
            print(data)


for ip in DGZ_IP:
    sdks.append(adc120sdk.AdcControl())
    sdks[-1].connect_data(ip)

for idx, sdk in enumerate(sdks):
    threading.Thread(target=thread_readout_function, args=(sdk,)).start()

while 1:
    time.sleep(1)