###Concept and design by Julius Sachs. Logic by Andrew Powell. Copyright 2016

import os, glob, time
import RPi.GPIO as GPIO

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#thermometer system constants
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

#are the sprinklers running?
running = False #default setting says: no, they aren't running.

#constants for the control logic. they're abstracted up here so that they can be modified a little more easily.
ontemp = 80.0 #the temperature (in degrees farenheit) to turn on the sprinklers
offtemp = 75.0 #the temperature (in degrees farenheit) to turn off the sprinklers
sPin = [17] #a list of the pins on the raspberry pi that control the relays

#wherein the relay control pins are defined as their labeling on the board rather than from the firmware (so that it runs on different revisions of the RPi), then the pins are switched from listening for inputs to broadcasting outputs
GPIO.setmode(GPIO.BCM)
for pin in sPin:
	GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

#ngl this code was copy pasted from the thermometer's documentation, and modified just a little bit to remove unnecessary abstractions.
def read_temp():
	f = open(device_file, 'r')
	lines = f.readlines()
	f.close()
	while lines[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = read_temp_raw()
	equals_pos = lines[1].find('t=')
	if equals_pos != -1:
		temp_string = lines[1][equals_pos+2:]
		temp_c = float(temp_string) / 1000.0
		temp_f = temp_c * 9.0 / 5.0 + 32.0
		return temp_f

#this is the control loop. it is very simple.
while True:
	x = read_temp() #store the temperature in farenheit as the variable 'x'.
	print(x) #let us know what that temperature is.
	if x <= offtemp: #oh wow! it's getting a little chilly! don't want sprinklers running.
		running = False
	if x >= ontemp: #oh jeez, it's getting kinda warm! why don't we turn on those sprinklers?
		running = True
	for pin in sPin: #that list of relay pins is a list. now we're looking at each pin in the list.
		GPIO.output(pin, running) #set the state of the pin based on whether or not we want the sprinklers running.
	time.sleep(1) #wait 1 second before going through the loop again. no need to go crazy with this.

GPIO.cleanup() #we're done running the sprinklers, so let's set the pins all back to their default state. don't want to short anything out accidentaly now, do we?
