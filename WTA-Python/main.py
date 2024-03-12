#!/usr/bin/python3

import random

import pydub.generators
from pydub import AudioSegment
from pydub.playback import play
import serial
import re
import sys

class Principal:
    enabled = False # whether this Principal is being played right now
    key = 0 # 0 to 11 in half-steps, 0 is the original key - keep track of transposition
    name = ''
    melody = [] # list of notes in the melody
    pos = 0 # current position in the melody

    '''
    Constructor - pass in a name and a melody array
    '''
    def __init__(self, name, melody):
        self.name = name
        self.melody = melody

    '''
    Transpose the melody by a number of half-steps, positive or negative
    '''
    def transpose(self, halfsteps):
        self.key += halfsteps

    '''
    Enable this Principal to be played.
    Also restarts the Principal's position but maintains transposition.
    '''
    def enable(self):
        self.pos = 0
        self.enabled = True

    '''
    Disable this Principle.
    '''
    def disable(self):
        self.enabled = False

    '''
    Play the next note in the melody.

    Pass in the "tempo," but this is the period of time in milliseconds that the note should be played.

    Returns the audio segment of the note, or False if the Principal is resting.

    TODO: figure out how to handle notes that are held...
    '''
    def play(self, tempo):
        if(self.enabled):
            self.pos = (self.pos+1) % len(self.melody)
            nextNote = self.melody[self.pos]
            if(nextNote == 'R'):
                print(self.name + " is resting")
                return False
            else:
                nextNote += self.key
            noteHz = self.noteToHz(nextNote)
            print(self.name + " will play " + str(nextNote) + " at " + str(noteHz) + "Hz")
            # playing with different waveforms:
            return pydub.generators.Square(noteHz,sample_rate=11025).to_audio_segment(tempo/2.0) # i like this one best :)
            #return pydub.generators.Sine(noteHz).to_audio_segment(tempo/2.0) # this one does not sound good - unclear intervals
            #return pydub.generators.Sawtooth(noteHz, sample_rate=11025).to_audio_segment(tempo/2.0) # feels very digital, a little buzzier than square wave but still nice
            #return pydub.generators.Triangle(noteHz).to_audio_segment(tempo/2.0) #also has bad interval sounds
        else:
            print(self.name + " is not enabled")
            return False

    '''
    Helper method to convert a note to a frequency in Hz.
    '''
    def noteToHz(self, note):
        print(note)
        xFormed = 440.0 * (2 ** ((note-10)/12))
        print(xFormed)
        return xFormed

# todo: fix this
def process_serial_input(s: serial.Serial):
    # T[0],E[0],D[0],H[0],L[0]
    t, e, d, h, l = None, None, None, None, None
    raw_serial = s.readline()
    print(raw_serial)
    out = []
    for bytes_string in  raw_serial.split(b","):
        end = bytes_string.find(b"]")
        out.append(int(bytes_string[2:end]))
    print(out)
    t = out[0]
    e = out[1]
    d = out[2]
    h = out[3]
    l = out[4]
    return t, e, d, h, l

principals = []
def setupPrincipals():
    global principals

    # For now just stick in some notes. Refer to WTC repertoire later on.
    melody1 = [1, 3, 5, 6, 8, 10, 12, 13, 12, 10, 8, 6, 5, 3, 1]
    melody2 = [13, 12, 10, 8, 6, 5, 3, 1, 'R']
    #melody1 = [1, 1, 1, 'R', 1, 1]
    #melody2 = [8, 8, 'R', 8, 8, 8]
    principal1 = Principal("Test 1", melody1)
    principal2 = Principal("Test 2", melody2)
    printipal1 = principal1.transpose(7)
    principals.append(principal1)
    principals.append(principal2)

def setupSerial():
    ser = serial.Serial()
    ser.baudrate = 9600
    # Choose port based on OS:
    if sys.platform.startswith('win'):
        ser.port = 'COM5'
    else:
        ser.port = '/dev/ttyACM0'
    ser.timeout = 0.25
    ser.open()
    return ser

if __name__ == "__main__":
    setupPrincipals()

    # For now, just enable all Principal objects in the array
    for p in principals:
        p.enable()

    # Set up serial port
    # ser = setupSerial()

    while True:
        # poll serial port
        #if ser.in_waiting:
        #    process_serial_input(ser)

        # play the next note for each enabled Principal, maintaining timing
        output = AudioSegment.silent(duration=250)
        for p in principals:
            note = p.play(250) #todo: calculate note period
            if(note):
                output = output.overlay(note)
        play(output)
    ser.close()
