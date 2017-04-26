#/usr/bin/env python
import pyaudio
from numpy import zeros,linspace,short,fromstring,hstack,transpose,log2, log
from scipy import fft, signal
from time import sleep
from scipy.signal import hamming, convolve
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO
import sys
#from findfundfreq import *
#Volume Sensitivity, 0.05: Extremely Sensitive, may give false alarms
#             0.1: Probably Ideal volume
#             1: Poorly sensitive, will only go off for relatively loud
SENSITIVITY= 1.0
#Bandwidth for detection (i.e., detect frequencies within this margin of error of the TONE)
BANDWIDTH = 1
# Show the most intense frequency detected (useful for configuration)
frequencyoutput=True

#notes in cents
Note_E = 5
Note_A = 0
Note_D = 7
Note_G = 2
Note_B = 10
Note_E4= 5


#holds previous frequency
prevFreq = 0
z1 = 10
z2 = 0
z0 = 0
MIN_FREQUENCY = 60
MAX_FREQUENCY = 500
#Max & Min cent value we care about
MAX_CENT = 11
MIN_CENT = 0
RELATIVE_FREQ = 440.0
if len(sys.argv) > 1:
	if (sys.argv[1] >= 415.0 and sys.argv[1] <= 445.0):
		RELATIVE_FREQ = sys.argv[1]

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
    intensity = abs(w*fft(normalized_data))[:NUM_SAMPLES/2]

    if frequencyoutput:
        which = intensity[1:].argmax()+1
        # use quadratic interpolation around the max
        adjfreq = 1
	if which != len(intensity)-1:
            y0,y1,y2 = log(intensity[which-1:which+2:])
            x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
	    # find the frequency and output:w it
            thefreq = (which+x1)*SAMPLING_RATE/NUM_SAMPLES
	    if thefreq < MIN_FREQUENCY or thefreq > MAX_FREQUENCY:
            	adjfreq = -9999
   	    else:
           	 thefreq = which*SAMPLING_RATE/NUM_SAMPLES
	    	 if thefreq > MIN_FREQUENCY:
            		adjfreq = thefreq
  	    #adjfreq = 140    
	#print("Candidate Freq:  ", candidate_freq, which )
	#sys.stdout.write("Frequency: %d  \r" % (adjfreq))
	#sys.stdout.flush()
	#cents conversion
	if (adjfreq != -9999):
		#print "RAW FREQ:", adjfreq
		adjfreq = 1200 *log2(RELATIVE_FREQ/adjfreq)/100
		adjfreq = adjfreq % 12
		#print adjfreq
		#Case statements
		if abs(adjfreq - Note_E4 ) < 1:
			
			#In Tune E
			if abs(adjfreq - Note_E4) < 0.1  :
				print("You played an E!")
				GPIO.output(5, GPIO.LOW)
				GPIO.output(6, GPIO.LOW)
				GPIO.output(13, GPIO.HIGH) #GREEN
			#Sharp E
			elif (adjfreq - Note_E4) <  0  :
				print("You are sharp E!")
				GPIO.output(5, GPIO.HIGH) #RED
				GPIO.output(6, GPIO.LOW) 
				GPIO.output(13, GPIO.LOW) 
			#Flat E
			elif (adjfreq - Note_E4) > 0  :
				print("You are flat E!")
				GPIO.output(5, GPIO.LOW)
				GPIO.output(6, GPIO.HIGH) #BLUE
				GPIO.output(13, GPIO.LOW)
		elif abs(adjfreq - Note_E ) < 1:
				
			#In Tune E
			if abs(adjfreq - Note_E) < 0.1  :
				print("You played an E2!")
				GPIO.output(5, GPIO.LOW)
				GPIO.output(6, GPIO.LOW)
				GPIO.output(13, GPIO.HIGH)
			#Sharp E
			elif (adjfreq - Note_E) < 0  :
				print("You are sharp E2!")
				GPIO.output(5, GPIO.HIGH) #RED
				GPIO.output(6, GPIO.LOW) 
				GPIO.output(13, GPIO.LOW) 
			#Flat E
			elif (adjfreq - Note_E) > 0  :
				print("You are flat E2!")
				GPIO.output(5, GPIO.LOW)
				GPIO.output(6, GPIO.HIGH) #BLUE
				GPIO.output(13, GPIO.LOW)
		elif abs(adjfreq - Note_B ) < 1:
			
			#In Tune B
			if abs(adjfreq - Note_B) < 0.1  :
				print("You played a B!")
				GPIO.output(5, GPIO.LOW)
				GPIO.output(6, GPIO.LOW)
				GPIO.output(13, GPIO.HIGH)
			#Sharp B
			elif (adjfreq - Note_B) < 0  :
				print("You are sharp (B)!")
				GPIO.output(5, GPIO.HIGH) #RED
				GPIO.output(6, GPIO.LOW) 
				GPIO.output(13, GPIO.LOW) 
			#Flat B
			elif (adjfreq - Note_B)  >0  :
				print("You are flat (B)!")
				GPIO.output(5, GPIO.LOW)
				GPIO.output(6, GPIO.HIGH) #BLUE
				GPIO.output(13, GPIO.LOW)
		elif abs(adjfreq - Note_G ) < 1:
			
			#In Tune g
			if abs(adjfreq - Note_G) < 0.1  :
				print("You played a G!")
				GPIO.output(5, GPIO.LOW)
				GPIO.output(6, GPIO.LOW)
				GPIO.output(13, GPIO.HIGH) #GREEN
			#Sharp G
			elif (adjfreq - Note_G) < 0  :
				print("You are sharp (G)!")
				GPIO.output(5, GPIO.HIGH) #RED
				GPIO.output(6, GPIO.LOW) 
				GPIO.output(13, GPIO.LOW) 
			#Flat G
			elif (adjfreq - Note_G) > 0  :
				print("You are flat (G)!")
				GPIO.output(5, GPIO.LOW)
				GPIO.output(6, GPIO.HIGH) #BLUE
				GPIO.output(13, GPIO.LOW)
		
		elif abs(adjfreq - Note_D ) < 1:
	
			GPIO.output(5, GPIO.LOW)
			GPIO.output(6, GPIO.LOW)
			GPIO.output(13, GPIO.HIGH)
			
			#In Tune D
			if abs(adjfreq - Note_D) < 0.1  :
				print("You played a D!")
				GPIO.output(5, GPIO.LOW)
				GPIO.output(6, GPIO.LOW)
				GPIO.output(13, GPIO.HIGH) #GREEN
			#Sharp D
			elif (adjfreq - Note_D) < 0  :
				print("You are sharp (D)!")
				GPIO.output(13, GPIO.LOW)
				GPIO.output(5, GPIO.HIGH) #RED
				GPIO.output(6, GPIO.LOW) 
			#Flat D
			elif (adjfreq - Note_D) > 0  :
				print("You are flat (D)!")
				GPIO.output(5, GPIO.LOW)
				GPIO.output(6, GPIO.HIGH) #BLUE
				GPIO.output(13, GPIO.LOW) 
		elif abs(adjfreq - Note_A ) < 1:
			
			#In tune A
			if abs(adjfreq - Note_A) < 0.2  :
				print("You played an A!")
				GPIO.output(5, GPIO.LOW)
				GPIO.output(6, GPIO.LOW)
				GPIO.output(13, GPIO.HIGH) #GREEN
			#Sharp A
			elif (adjfreq - Note_A) < 0  :
				print("You are sharp A!")
				GPIO.output(13, GPIO.LOW)
				GPIO.output(5, GPIO.HIGH) #RED
				GPIO.output(6, GPIO.LOW) 
			#Flat A
			elif (adjfreq - Note_A)  > 0  :
				print("You are flat A!")
				GPIO.output(5, GPIO.LOW)
				GPIO.output(6, GPIO.HIGH) #BLUE
				GPIO.output(13, GPIO.LOW)
		elif abs(adjfreq - 12 ) < 1:
			
			#In tune A
			if abs(adjfreq - 12) < 0.2  :
				print("You played an A!")
				GPIO.output(5, GPIO.LOW)
				GPIO.output(6, GPIO.LOW)
				GPIO.output(13, GPIO.HIGH) #GREEN
			#Sharp A
			elif (adjfreq - 12) < 0  :
				print("You are sharp A!")
				GPIO.output(13, GPIO.LOW)
				GPIO.output(5, GPIO.HIGH) #RED
				GPIO.output(6, GPIO.LOW) 
			#Flat A
			elif (adjfreq - 12)  > 0  :
				print("You are flat A!")
				GPIO.output(5, GPIO.LOW)
				GPIO.output(6, GPIO.HIGH) #BLUE
				GPIO.output(13, GPIO.LOW)
  	#all off
	else:
		GPIO.output(5, GPIO.LOW) 
		GPIO.output(6, GPIO.LOW)
		GPIO.output(13, GPIO.LOW)
	#sys.stdout.write("Cent: %s  \r" % adjfreq)
	#sys.stdout.flush()
		
	sleep(0.01)
