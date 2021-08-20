import mcp3008_emg as ms
import time
import datetime 
import threading
import pandas as pd
import schedule

fileName = time.strftime('%y%m%d_%H%M%S')

f = open('../csv/emg_'+fileName+'.csv',"w")

count = 0

arr_header = 'time'

EMG = 0
Envelope = 1

mcp_emg = ms.set_mcp(EMG)
mcp_env = ms.set_mcp(Envelope)

f.write('Time,EMG,Envelope\n')
now1 = datetime.datetime.now()

print(now1)

start = time.time()

def ReadValue():
    global count
    
    #ti = time.strftime('%y%m%d%H%M%S%f', time.localtime(time.time()))
    t2 = datetime.datetime.now().strftime('%y%m%d%H%M%S%f')[:-3]
    #dt = datetime.datetime.now().microsecond
    print ("Time: ",datetime.datetime.now())
    
    emg = ms.readAnalog(mcp_emg, EMG)
    env = ms.readAnalog(mcp_env,Envelope)
    
    f.write((str(t2))+','+str(emg)+','+str(env)+'\n')
    count += 1

    timer = threading.Timer(0.01,ReadValue)
    timer.start()
    #schedule.every(1).second.do(ReadValue())
    
    if count == 1000:
        timer.cancel()
        f.close()
        
ReadValue()

