#!/usr/bin/env python
import pyaudio
from numpy import zeros,linspace,short,fromstring,hstack,transpose,log
from scipy import fft, signal
from time import sleep
from scipy.signal import hamming, convolve
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO
#Volume Sensitivity, 0.05: Extremely Sensitive, may give false alarms
#             0.1: Probably Ideal volume
#             1: Poorly sensitive, will only go off for relatively loud
SENSITIVITY= 1.0
#Bandwidth for detection (i.e., detect frequencies within this margin of error of the TONE)
BANDWIDTH = 5
# Show the most intense frequency detected (useful for configuration)
frequencyoutput=True

Note_E = 82.41 
Note_A = 110.00
Note_D = 146.8
Note_G = 196.0
Note_B = 246.9
Note_E4= 329.6

#holds previous frequency
prevFreq = 0

MIN_FREQUENCY = 20
MAX_FREQUENCY = 100
#FLAT_BOUND = 
#SHARP_BOUND = 

#GPIO set up for the Red Green and Blue colors
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)

#Set up audio sampler - 
NUM_SAMPLES = 2048
SAMPLING_RATE = 48000
pa = pyaudio.PyAudio()
_stream = pa.open(format=pyaudio.paInt16,
                  channels=1, rate=SAMPLING_RATE,
                  input=True,
                  frames_per_buffer=NUM_SAMPLES)

print("Detecting Frequencies. Press CTRL-C to quit.")
go = 10
#while go > 0:
while True:
    while _stream.get_read_available()< NUM_SAMPLES: sleep(0.01)
    audio_data  = fromstring(_stream.read(
         _stream.get_read_available()), dtype=short)[-NUM_SAMPLES:]
    # Each data point is a signed 16 bit number, so we can normalize by dividing 32*1024
    normalized_data = audio_data / 32768.0
    w = hamming(2048)
    #intensity = abs(fft(convolve(normalized_data,w, mode='same')))[:NUM_SAMPLES/2]
#    w_fft = fft(w)


    candidate = 0
    intensity = abs(fft(normalized_data))[:NUM_SAMPLES/2]



    if frequencyoutput:
        which = intensity[1:].argmax()+1
        if(which > 2): 
		candidate = intensity[1:which-1].argmax()+1
	#	print("WHICH  ", which)
	#	print("CANDIDATE ", candidate)
        # use quadratic interpolation around the max
        adjfreq = 0
	if which != len(intensity)-1:
            y0,y1,y2 = log(intensity[which-1:which+2:])
            x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
      	    if(which > 2): 
            	z0,z1,z2 = log(intensity[candidate-1:candidate+2:])
            	r1 = (z2 - z0) * .5 / (2 * z1 - z2 - z0)
            
	    # find the frequency and output:w it
            thefreq = (which+x1)*SAMPLING_RATE/NUM_SAMPLES
            candidate_freq = (candidate+x1)*SAMPLING_RATE/NUM_SAMPLES
	    print "CANDIDATE_FREQ: ", candidate_freq
	    if (candidate_freq >= thefreq/2 + 10 and candidate_freq <= thefreq/2-10):
		thefreq = candidate_freq
	    if thefreq > MIN_FREQUENCY:
            	adjfreq = thefreq
        else:
            thefreq = which*SAMPLING_RATE/NUM_SAMPLES
	    if thefreq > MIN_FREQUENCY:
            	adjfreq = thefreq

	#if abs(adjfreq - prevfreq) > 10: 
	#	prevfreq = adjfreq
        print "\t\t\t\tfreq=",adjfreq
	if adjfreq <= (Note_E4 + BANDWIDTH) and adjfreq >= (Note_E4 - BANDWIDTH):
		print("You played an E4!")
		GPIO.output(5, GPIO.LOW)
		GPIO.output(6, GPIO.LOW)
		delay = 200
		while(delay>0):
			GPIO.output(13, GPIO.HIGH)
			delay = delay -0.5
	elif adjfreq <= (Note_B + BANDWIDTH) and adjfreq >= (Note_B - BANDWIDTH):
		print("You played an B!")
		GPIO.output(5, GPIO.LOW)
		GPIO.output(6, GPIO.LOW)
		delay = 200
		while(delay>0):
			GPIO.output(13, GPIO.HIGH)
			delay = delay -1
	elif adjfreq <= (Note_G + BANDWIDTH) and adjfreq >= (Note_G - BANDWIDTH):
		print("You played an G!")
		GPIO.output(5, GPIO.LOW)
		GPIO.output(6, GPIO.LOW)
		delay = 200
		while(delay>0):
			GPIO.output(13, GPIO.HIGH)
			delay = delay -1
	elif adjfreq <= (Note_D + BANDWIDTH) and adjfreq >= (Note_D - BANDWIDTH):
		print("You played an D!")
		GPIO.output(5, GPIO.LOW)
		GPIO.output(6, GPIO.LOW)
		delay = 200
		while(delay>0):
			GPIO.output(13, GPIO.HIGH)
			delay = delay -1
	elif adjfreq <= (Note_A + BANDWIDTH) and adjfreq >= (Note_A - BANDWIDTH):
		print("You played an A!")
		GPIO.output(5, GPIO.LOW)
		GPIO.output(6, GPIO.LOW)
		delay = 200
		while(delay>0):
			GPIO.output(13, GPIO.HIGH)
			delay = delay -1
	elif adjfreq <= (Note_E + BANDWIDTH) and adjfreq >= (Note_E - BANDWIDTH):
		print("You played an E2!")
		GPIO.output(5, GPIO.LOW)
		GPIO.output(6, GPIO.LOW)
		delay = 200
		while(delay>0):
			GPIO.output(13, GPIO.HIGH)
			delay = delay -1
	#Sharp E4
	elif adjfreq >= (Note_E4 + BANDWIDTH) and adjfreq < MAX_FREQUENCY:
		print("You are sharp (E4) !")
		GPIO.output(5, GPIO.LOW)
		GPIO.output(6, GPIO.HIGH) #RED
		GPIO.output(13, GPIO.LOW)
	#Flat E4
	elif adjfreq <= (Note_E4 - BANDWIDTH) and adjfreq >= 311 :
		print("You are flat (E4) !")
		GPIO.output(5, GPIO.HIGH) #BLUE
		GPIO.output(6, GPIO.LOW)
		GPIO.output(13, GPIO.LOW)
	#Sharp B
	elif adjfreq >= (Note_B + BANDWIDTH) and adjfreq <= 250:
		print("You are sharp (B) !")
		GPIO.output(5, GPIO.LOW)
		GPIO.output(6, GPIO.HIGH) #RED
		GPIO.output(13, GPIO.LOW)
	#Flat B
	elif adjfreq <= (Note_G - BANDWIDTH) and adjfreq > 233 :
		print("You are flat (B)!")
		GPIO.output(5, GPIO.HIGH) #BLUE
		GPIO.output(6, GPIO.LOW)
		GPIO.output(13, GPIO.LOW)
	#Sharp G
	elif adjfreq >= (Note_G + BANDWIDTH) and adjfreq <= ((Note_B-Note_G)/2):
		print("You are sharp (G)!")
		GPIO.output(5, GPIO.LOW)
		GPIO.output(6, GPIO.HIGH) #RED
		GPIO.output(13, GPIO.LOW)
	#Flat G
	elif adjfreq <= (Note_G - BANDWIDTH) and adjfreq > ((Note_G - Note_D)/2) :
		print("You are flat (G) !")
		GPIO.output(5, GPIO.HIGH) #BLUE
		GPIO.output(6, GPIO.LOW)
		GPIO.output(13, GPIO.LOW)
	#Sharp D
	elif adjfreq >= (Note_D + BANDWIDTH) and adjfreq <= ((Note_G-Note_D)/2):
		print("You are sharp (D)!")
		GPIO.output(5, GPIO.LOW)
		GPIO.output(6, GPIO.HIGH) #RED
		GPIO.output(13, GPIO.LOW)
	#Flat D
	elif adjfreq <= (Note_D - BANDWIDTH) and adjfreq > ((Note_D - Note_A)/2) :
		print("You are flat (D)!")
		GPIO.output(5, GPIO.HIGH) #BLUE
		GPIO.output(6, GPIO.LOW)
		GPIO.output(13, GPIO.LOW)
	#Sharp A
	elif adjfreq >= (Note_A + BANDWIDTH) and adjfreq <= ((Note_D-Note_A)/2):
		print("You are sharp (A)!")
		GPIO.output(5, GPIO.LOW)
		GPIO.output(6, GPIO.HIGH) #RED
		GPIO.output(13, GPIO.LOW)
	#Flat A
	elif adjfreq <= (Note_A - BANDWIDTH) and adjfreq > ((Note_A - Note_E)/2) :
		print("You are flat (A)!")
		GPIO.output(5, GPIO.HIGH) #BLUE
		GPIO.output(6, GPIO.LOW)
		GPIO.output(13, GPIO.LOW)
	#Sharp E
	elif adjfreq >= (Note_E + BANDWIDTH) and adjfreq <= ((Note_A-Note_E)/2):
		print("You are sharp (E2)!")
		GPIO.output(5, GPIO.LOW)
		GPIO.output(6, GPIO.HIGH) #RED
		GPIO.output(13, GPIO.LOW)
	#Flat E
	elif adjfreq <= (Note_E - BANDWIDTH) and adjfreq > MIN_FREQUENCY :
		print("You are flat (E2)!")
		GPIO.output(5, GPIO.HIGH) #BLUE
		GPIO.output(6, GPIO.LOW)
		GPIO.output(13, GPIO.LOW)
    	#all off
	else:
		GPIO.output(5, GPIO.LOW) 
		GPIO.output(6, GPIO.LOW)
		GPIO.output(13, GPIO.LOW)
		
	sleep(0.01)
	go = go -1
