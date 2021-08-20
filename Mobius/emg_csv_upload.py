import mcp3008_emg as ms
import time
import threading
import pandas as pd
import schedule
import change_filename as fn
from datetime import datetime
import requests
import pandas as pd
import numpy as np

filename = time.strftime('%y%m%d_%H%M%S')
f = open('./csv/EMG_'+filename+'.csv',"w")

EMG = 0
Envelope = 1
NUM = 20

count = 0

mcp_emg = ms.set_mcp(EMG)
mcp_env = ms.set_mcp(Envelope)

f.write('time,emg,envelope'+'\n')

def ReadValue():
	global count

	emg_val = ms.readAnalog(mcp_emg, EMG)
	env_val = ms.readAnalog(mcp_env, Envelope)

	time = datetime.now().strftime('%y%m%d_%H:%M:%S.%f')[:-3]

	f.write(str(time) + ',' + str(emg_val) + ',' + str(env_val)+'\n')	
	count += 1

	# threading
	timer = threading.Timer(0.06, ReadValue)
	timer.start()

	if count == NUM:
		timer.cancel()

		f.close()

		post('emg')
		post('envelope')

def post(value):
	df = pd.read_csv("./csv/EMG_"+filename+".csv", encoding="UTF-8")
	
	t = df.loc[:NUM, 'time']
	va = t[0] + "," + t[NUM-1]

	v = df.loc[:NUM, value]
	for i in range(NUM):
		va = va + "," + str(v[i])

	url = "http://203.253.128.177:7579/Mobius/healthcare-interworking/emg/" + value

	cin_contents = va

	payload = "{\n    \"m2m:cin\": {\n        \"con\": \"" + str(cin_contents) + "\"\n    }\n}"
	headers = {
	'Accept': 'application/json',
	'X-M2M-RI': '12345',
	'X-M2M-Origin': '{{aei}}',
	'Content-Type': 'application/vnd.onem2m-res+json; ty=4'
	}

	response = requests.request("POST", url, headers=headers, data=payload)

	print(response.text)

ReadValue()
