import RPi.GPIO as GPIO
from AlphaBot2 import AlphaBot2
from TRSensors import TRSensor
import time
import numpy as np
from scipy.stats import iqr

TR = TRSensor()
Ab = AlphaBot2()

def mediaValori(listValues):#accetta in input l'array del dizionario

    #TOR PARTE DI CALCOLO DEI DATI
    moltiplicatore = 0.1
    misurazioni = np.array(listValues)
    q1 = np.percentile(misurazioni, 45) 
    q3 = np.percentile(misurazioni, 55) 

    iqr_value = iqr(misurazioni) 

    soglia_inf = q1 - moltiplicatore * iqr_value 
    soglia_sup = q3 + moltiplicatore * iqr_value

    #li filtro
    misurazioni_filtrate = misurazioni[(misurazioni >= soglia_inf) & (misurazioni <= soglia_sup)]

    return np.mean(misurazioni_filtrate, dtype=np.int64) #faccio la media tra tutti i valori dell'array

def calibration():
	input("Quando mi hai messo sul nero batti invio")
	inizio = time.time()
	limit = []
	while time.time() - inizio < 3:
		Sensors = TR.AnalogRead()
		limit.append(Sensors)

	limit = np.array(limit)
	mean_values = []
	for i in range(len(limit[0])):
		mean_values.append(mediaValori(limit[::,i])+ 60)
	return mean_values



def line_tracker(SOGLIE):
	Sensors = TR.AnalogRead()
	print(Sensors)
	direction = np.array(Sensors) < SOGLIE

	while not(direction[0] and direction[1] and direction[2] and direction[3] and direction[4]):
		Sensors = TR.AnalogRead()
		#print(Sensors)
		direction = np.array(Sensors) < SOGLIE
		#print(direction)
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


	
		
	
	
