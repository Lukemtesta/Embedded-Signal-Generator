'''
Prototype python for proof-of-concept before arduino port

Some design patterns and python functionalities are not used on purpose (e.g. abstract factory, 
linspace etc.) because equivalent operations are not supported on the arduino. Alternatives are 
used (i.e. abstract factory instead uses dispatcher via function pointer, easier to achieve in C.
'''

import os
import math
import numpy 
import argparse
import matplotlib.pyplot as plt

'''
Normalise a non-periodic value 
@param[in]  val       value to normalise
@param[in]  maxval    maximum possible value
@param[in]  minval    minimum possible value
'''
def Normalise(val, maxval, minval):

    return (val - minval) / (maxval - minval)

'''
Normalise a periodic value between its minimum and maximum 
@param[in]  val       value to normalise
@param[in]  maxval    maximum possible value
@param[in]  minval    minimum possible value
'''
def NormaliseMinToMax(val, maxval, minval):

    ret = Normalise(val, maxval, minval)
    return ret - math.floor(ret)

'''
Computes a sine wave. 
@param[in]  amplitude       Amplitude of signal
@param[in]  frequency       Rate of signal
@param[in]  phase           time shift between 0 and 1
@param[in]  ts              unsigned timestamp
@param[in]  samplingrate    Sampling rate of signal, min x2 frequency
'''
def CreateSine(amplitude, frequency, phase, ts, samplingrate):

    phase *= 2 * math.pi
    coeff = 2 * math.pi * frequency * (ts / samplingrate)

    return amplitude * math.sin(coeff + phase)
    
'''
Computes a square. 
@param[in]  amplitude       Amplitude of signal
@param[in]  frequency       Rate of signal
@param[in]  phase           time shift between 0 and 1
@param[in]  ts              unsigned timestamp
@param[in]  samplingrate    Sampling rate of signal, min x2 frequency
'''
def CreateSquare(amplitude, frequency, phase, ts, samplingrate):

    val = CreateSine(amplitude, frequency, phase, ts, samplingrate)
    
    return numpy.sign(val) * amplitude
    
'''
Computes a triangle. 
@param[in]  amplitude       Amplitude of signal
@param[in]  frequency       Rate of signal
@param[in]  phase           time shift between 0 and 1
@param[in]  ts              unsigned timestamp
@param[in]  samplingrate    Sampling rate of signal, min x2 frequency
'''
def CreateTriangle(amplitude, frequency, phase, ts, samplingrate):

    # Not using linspace because target device (arduino) doesn't support linspace
    offset = NormaliseMinToMax(phase + .25, 1, 0) * samplingrate
    t = NormaliseMinToMax(ts + offset, samplingrate, 0)
    
    # scale by... max t = .5, so 2 + (-V -> +V = 2 * am) => scale by 4)
    scale = amplitude * 4
    ret = t * scale
    
    if(t > .5):
        ret = scale - ret
        
    ret -= amplitude

    # Apply negative bias to pull down from min(0) to min(-Am)
    return ret
    
'''
Computes a sawtooth. 
@param[in]  amplitude       Amplitude of signal
@param[in]  frequency       Rate of signal
@param[in]  phase           time shift between 0 and 1
@param[in]  ts              unsigned timestamp
@param[in]  samplingrate    Sampling rate of signal, min x2 frequency
'''
def CreateSawtooth(amplitude, frequency, phase, ts, samplingrate):

    # Not using linspace because target device (arduino) doesn't support linspace
    offset = NormaliseMinToMax(phase - .5, 1, 0) * samplingrate
    t = NormaliseMinToMax(ts + offset, samplingrate, 0)
    
    return (t * amplitude * 2) - amplitude

'''
Execute waveform method
@param[in]  func            function to execute
@param[in]  amplitude       Amplitude of signal
@param[in]  frequency       Rate of signal
@param[in]  phase           time shift between 0 and 1
@param[in]  interal         timestamp intervals
'''
def CreateWaveform(func, amplitude, frequency, phase, interval = .01):

    samplingrate = 4 * args.frequency;

    ret = []
    for i in range(0, int(frequency / interval)):
        ret.append(func(args.amplitude, frequency * interval, phase, i, samplingrate))
        
    return ret
    
'''
Parse command line params
'''
def ParseCmdParams():

    parser = argparse.ArgumentParser()

    parser.add_argument(
    '--am', 
    dest='amplitude',
    help='Amplitude', 
    type=float, 
    required=False,
    default=1)
    
    parser.add_argument(
    '--fr', 
    dest='frequency',
    help='frequency',
    type=float, 
    required=False, 
    default=1)
    
    parser.add_argument(
    '--ph', 
    dest='phase',
    help='phase', 
    type=float, 
    required=False,
    default = 0)

    return parser.parse_args()
    

'''
Application entry point
'''
if __name__ == "__main__":

    args = ParseCmdParams()
    
    sine = CreateWaveform(CreateSine, args.amplitude, args.frequency, args.phase)
    square = CreateWaveform(CreateSquare, args.amplitude, args.frequency, args.phase)
    sawtooth = CreateWaveform(CreateSawtooth, args.amplitude, args.frequency, args.phase)
    triangle = CreateWaveform(CreateTriangle, args.amplitude, args.frequency, args.phase)
    
    a, = plt.plot(sine, 'r')
    b, = plt.plot(square, 'b')
    c, = plt.plot(sawtooth, 'y')
    d, = plt.plot(triangle, 'k')
    plt.ylabel('Amplitude (V)')
    plt.xlabel('Timestamp (s)')
    plt.legend([a, b, c, d], ['Sine', 'Square', 'Sawtooth', 'Triangle'])
    plt.title('Frequency = ' + str(args.frequency) + ', Amplitude = ' + str(args.amplitude) + ', Phase = ' + str(args.phase))
    plt.show()