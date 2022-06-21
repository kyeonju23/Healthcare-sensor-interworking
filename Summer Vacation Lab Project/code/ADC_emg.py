import mcp3008_emg as ms
import time

EMG = 0
Envelope = 1

mcp_emg = ms.set_mcp(EMG)
mcp_env = ms.set_mcp(Envelope)

while 1:
	emg = ms.readAnalog(mcp_emg,EMG)
	env = ms.readAnalog(mcp_env,Envelope)

	print("EMG: ", emg)
	print("Env: ", env)

	time.sleep(1)
