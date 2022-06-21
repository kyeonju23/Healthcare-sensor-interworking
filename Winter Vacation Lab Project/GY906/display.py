import time ,  datetime

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import RPi.GPIO as GPIO

#import GY906 as GY906

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import smbus2
import subprocess
# from gy960 import GY906 
# from gy960 import main as GY906
#from gy960 import GY906

# Raspberry Pi pin configuration:
RST = 24     
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
font = ImageFont.load_default()
font1 = ImageFont.truetype('rainyhearts.ttf', 15)
font2 = ImageFont.truetype('VCR_OSD_MONO_1.001.ttf', 23)

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 8)

dateString = '%a %D'
timeString = '%H:%M:%S'


class GY906(object):

	MLX90614_RAWIR1=0x04
	MLX90614_RAWIR2=0x05
	MLX90614_TA=0x06
	MLX90614_TOBJ1=0x07
	MLX90614_TOBJ2=0x08
	MLX90614_TOMAX=0x20
	MLX90614_TOMIN=0x21
	MLX90614_PWMCTRL=0x22
	MLX90614_TARANGE=0x23
	MLX90614_EMISS=0x24
	MLX90614_CONFIG=0x25
	MLX90614_ADDR=0x0E
	MLX90614_ID1=0x3C
	MLX90614_ID2=0x3D
	MLX90614_ID3=0x3E
	MLX90614_ID4=0x3F

	def __init__(self, address=0x5a, bus_num=1, units = "c"):
		self.bus_num = bus_num
		self.address = address
		self.bus = smbus2.SMBus(bus=bus_num)
		self.units = units

	def read_reg(self, reg_addr):
		try :
			return self.bus.read_word_data(self.address, reg_addr)
		except:
			return None

	def pass_c(self, celsius):
		return celsius - 273.15

	def pass_k(self, celsius):
		return celsius

	def pass_f(self, celsius):
		return (celsius - 273.15) * 9.0/5.0 + 32

	def data_to_temp(self, data):
		temp = (data*0.02)
		temperature = getattr(self, "pass_" + self.units)(temp)
		return temperature

	def get_amb_temp(self):
		data = self.read_reg(self.MLX90614_TA)
		if data != None:
			return self.data_to_temp(data)
		else:
			return None

	def get_obj_temp(self):
		data = self.read_reg(self.MLX90614_TOBJ1)
		if data != None:
			return self.data_to_temp(data)
		else:
			return None

while True:
    sensor=GY906(0x5a,1,'c')
    temperature = float(sensor.get_obj_temp())
    temp = round(temperature,2)

    strDate = datetime.datetime.now().strftime(dateString)
    result  = datetime.datetime.now().strftime(timeString)

    draw.rectangle((0,0,width,height), outline=0, fill=0)

    draw.text((x,top+1),strDate, font=font1,fill=255)
    draw.text((x+90,top+1),str(temp), font=font1,fill=255)
    draw.text((x+10, top+12), str(temp),  font=font2, fill=255)

   # draw.line((0, top+12, 127, top+12), fill=100)

    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(.1)
