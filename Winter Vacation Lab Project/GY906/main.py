import GY906 as GY906
import time
from pymongo import MongoClient

#c = celsius
units = 'c'
bus = 1
address = 0x5a

sensor = GY906.GY906(address,bus,units)

time.sleep(1)
running = True

client = MongoClient('localhost', 27017) 
db = client.ubicomp

while(running):
    try:
        #get area temperature
        temperature_area = sensor.get_amb_temp()
        doc = {'type':'area', 'temperature': temperature_area} 
        db.gy906.insert_one(doc)
        #get object temperature
        temperature_obj = sensor.get_obj_temp()
        doc = {'type':'object', 'temperature':temperature_obj} 
        db.gy906.insert_one(doc)
        
        print ('Area Temp={0:0.1f} {1}'.format(temperature_area,units))
        print ('Obj Temp={0:0.1f} {1}'.format(temperature_obj,units))
        print()
    
        time.sleep(2)
    except KeyboardInterrupt:
        running = False