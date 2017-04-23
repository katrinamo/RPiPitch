#!/usr/bin/env python
import pyaudio
from numpy import diff, argmax, zeros,linspace,short,fromstring,hstack,transpose,log
from scipy import fft, signal
from time import sleep
from scipy.signal import hamming, fftconvolve
from matplotlib.mlab import find
from parabolic import parabolic

#Volume Sensitivity, 0.05: Extremely Sensitive, may give false alarms
#             0.1: Probably Ideal volume
#             1: Poorly sensitive, will only go off for relatively loud
SENSITIVITY= 1.0
#Bandwidth for detection (i.e., detect frequencies within this margin of error of the TONE)
BANDWIDTH = 10.0
# Show the most intense frequency detected (useful for configuration)
frequencyoutput=True



Note_E = 82.41 
Note_A = 110.00
Note_D = 146.8
Note_G = 196.0
Note_B = 246.9
Note_E4= 329.6


#Set up audio sampler - 
NUM_SAMPLES = 4096
SAMPLING_RATE = 44100
pa = pyaudio.PyAudio()
_stream = pa.open(format=pyaudio.paInt16,
                  channels=1, rate=SAMPLING_RATE,
                  input=True,
                  frames_per_buffer=NUM_SAMPLES)

print("Detecting Frequencies. Press CTRL-C to quit.")


while True:
    while _stream.get_read_available()< NUM_SAMPLES: sleep(0.01)
    audio_data  = fromstring(_stream.read(
         _stream.get_read_available()), dtype=short)[-NUM_SAMPLES:]
    # Each data point is a signed 16 bit number, so we can normalize by dividing 32*1024
    normalized_data = audio_data / 32768.0
    corr = fftconvolve(normalized_data, normalized_data[::-1], mode="full")
    corr = corr[len(corr)/2:]
    d = diff(corr)
    start = find(d>0)[0]
    i_peak = argmax(corr[start:])+start
    i_interp = parabolic(corr,i_peak)[0]
    adjfreq = normalized_data/i_interp


    print "\t\t\t\tfreq=",adjfreq
#   if adjfreq <= (Note_E4 + BANDWIDTH) and adjfreq >= (Note_E4 - BANDWIDTH):
#		print("You played an E4!")
#   elif adjfreq <= (Note_B + BANDWIDTH) and adjfreq >= (Note_B - BANDWIDTH):
#		print("You played an B!")
#    elif adjfreq <= (Note_G + BANDWIDTH) and adjfreq >= (Note_G - BANDWIDTH):
#		print("You played an G!")
#    elif adjfreq <= (Note_D + BANDWIDTH) and adjfreq >= (Note_D - BANDWIDTH):
#		print("You played an D!")
#    elif adjfreq <= (Note_A + BANDWIDTH) and adjfreq >= (Note_A - BANDWIDTH):
#		print("You played an A!")
#    elif adjfreq <= (Note_E + BANDWIDTH) and adjfreq >= (Note_E - BANDWIDTH):
#		print("You played an E2!")'''
    sleep(0.01)

