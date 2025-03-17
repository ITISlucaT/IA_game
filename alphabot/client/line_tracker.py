import RPi.GPIO as GPIO
from AlphaBot2 import AlphaBot2
from TRSensors import TRSensor
import time
import numpy as np

TR = TRSensor()
Ab = AlphaBot2()

SOGLIE = np.array([300, 10, 300, 350, 300])
def line_tracker():
	Sensors = TR.AnalogRead()
	print(Sensors)
	direction = np.array(Sensors) < SOGLIE

	while not(direction[0] and direction[1] and direction[2] and direction[3] and direction[4]):
		Sensors = TR.AnalogRead()
		print(Sensors)
		direction = np.array(Sensors) < SOGLIE
		print(direction)
		if direction[0] or direction[1]:
			Ab.setMotor(0,-30)
		elif direction[3] or direction[4]:
			Ab.setMotor(30, 0)
		elif direction[2]:
			Ab.setMotor(30, -30)
		
		else:
			Ab.stop()
		time.sleep(0.01)
	Ab.stop()

def handle_movements(direction):
	action_map = {
		0: "UP",
		1: "DOWN", 
		2: "LEFT", 
		3: "RIGHT"
	}
	if direction == "UP":
		Ab.setMotor(30,-30)
	elif direction == "LEFT":
		Ab.setMotor(30, 0)
	elif direction == "RIGHT":
		Ab.setMotor(0,-30)
	else:
		Ab.setMotor(30,30)
		time.sleep(0.5)
	time.sleep(0.5)

def dir_from_angle(direction, angle):
	ret = ""
	if angle == 0:
		if direction == "LEFT":
			ret = "RIGHT"
			angle = 90
		elif direction == "RIGHT":
			ret = "LEFT"
			angle = 270
		elif direction == "DOWN":
			ret = "UP"
		else:
			direction = "TURN_AROUND"
			angle = 180
	elif angle == 90:
		if direction == "LEFT":
			ret = "UP"
		elif direction == "RIGHT":
			ret = "TURN_AROUND"
			angle = 270
		elif direction == "DOWN":
			ret = "LEFT"
			angle = 0
		else:
			ret = "RIGHT"
			angle = 180
	elif angle == 180:
		if direction == "DOWN":
			ret = "TURN_AROUND"
			angle = 0
		else:
			ret = direction
			if direction == "RIGHT":
				angle = 270
			elif direction == "LEFT":
				angle = 90
	elif angle == 270:
		if direction == "LEFT":
			ret = "TURND_AROUND"
			angle = 90
		elif direction == "RIGHT":
			ret = "UP"
		elif direction == "DOWN":
			ret = "RIGHT"
			angle = 0
		else:
			ret == "LEFT"
			angle = 180
	return ret, angle
