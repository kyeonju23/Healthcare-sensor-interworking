import mcp3008_sa as ms
import time
import datetime 
import threading
import pandas as pd
import schedule

fileName = time.strftime('%y%m%d_%H%M%S')

f = open('./csv/Biometrix_'+fileName+'.csv',"w")

count = 0

arr_header = 'time'

EMG = 0
Envelope = 1
ECG = 2
ECG_BEAT = 3
PPG = 4
PPG_BEAT = 5

mcp_emg = ms.set_mcp(EMG)
mcp_env = ms.set_mcp(Envelope)
mcp_ecg = ms.set_mcp(ECG)
mcp_ecgbeat = ms.set_mcp(ECG_BEAT)
mcp_ppg = ms.set_mcp(PPG)
mcp_ppgbeat = ms.set_mcp(PPG_BEAT)

f.write('Time,EMG,Envelope,ECG,Beat_ecg,PPG,Beat_ppg\n')

now1 = datetime.datetime.now()

print(now1)

start = time.time()

def ReadValue():
    global count
    
    ti = datetime.datetime.now().strftime('%y%m%d%H%M%S%f')[:-3]
    
    print ("Time: ",datetime.datetime.now())
    
    emg = ms.readAnalog(mcp_emg, EMG)
    env = ms.readAnalog(mcp_env,Envelope)
    ecg = ms.readAnalog(mcp_ecg, ECG)
    ecgbeat = ms.readAnalog(mcp_ecgbeat, ECG_BEAT)
    ppg = ms.readAnalog(mcp_ppg, PPG)
    ppgbeat = ms.readAnalog(mcp_ppgbeat, PPG_BEAT)

    f.write((str(ti))+','+str(emg)+','+str(env)+','+str(ecg)+','+str(ecgbeat)+','+str(ppg)+','+str(ppgbeat)+'\n')
    count += 1

    timer = threading.Timer(0.01,ReadValue)
    timer.start()
    #schedule.every(1).second.do(ReadValue())
    
    if count == 100:
        timer.cancel()
        f.close()
        
ReadValue()

