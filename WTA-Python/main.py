#!/usr/bin/python3

import random

import pydub.generators
from pydub import AudioSegment
from pydub.playback import play
import serial
import re
import sys

class Subject:
    enabled = False # whether this Subject is being played right now
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
    Transpose the melody by a number of half-steps, positive or negative (relative!)
    '''
    def transpose(self, halfsteps):
        self.key += halfsteps

    '''
    Enable this Subject to be played.
    Also restarts the Subject's position and transposition.
    '''
    def enable(self):
        self.pos = 0
        self.key = 0
        self.enabled = True

    '''
    Disable this Subject.
    '''
    def disable(self):
        self.enabled = False

    '''
    Play the next note in the melody.

    Pass in the "tempo," but this is the period of time in milliseconds that the note should be played.

    Returns the audio segment of the note, or False if the Subject is resting.

    TODO: figure out how to handle notes that are held...?
    '''
    def play(self, tempo):
        if(self.enabled):
            self.pos = (self.pos+1) % len(self.melody)
            nextNote = self.melody[self.pos]
            if(nextNote == 'R'):
                print('I: ' + self.name + " is resting")
                return False
            else:
                nextNote += self.key
            noteHz = self.noteToHz(nextNote)
            print("I: "+self.name + " will play " + str(nextNote) + " at " + str(noteHz) + "Hz")
            # check for fast notes
            if self.melody[(self.pos + 1) % len(self.melody)] != '+':
                return pydub.generators.Square(noteHz,sample_rate=44100).to_audio_segment(duration=tempo/2.0, volume=-10) 

            segment = pydub.generators.Square(noteHz,sample_rate=44100).to_audio_segment(duration=tempo/4.0, volume=-10)
            
            self.pos = (self.pos+1) % len(self.melody)
            return segment + self.play(tempo/2.0)
        else:
            print('I: ' + self.name + " is disabled")
            return False

    '''
    Helper method to convert a note to a frequency in Hz.
    '''
    def noteToHz(self, note):
        xFormed = 440.0 * (2 ** ((note-10)/12))
        return xFormed

##############################
# global variables and more! #
##############################

# this is the list that'll hold all the Subject objects
subjects = []
# note: these are NOT bpm - it's the duration of the unit note
# in milliseconds. if you go too low the synthesis makes it
# sound kinda funny idk. note that higher values == longer notes.
MIN_DURATION = 100
MAX_DURATION = 1500
duration = MIN_DURATION

silence = AudioSegment.silent(duration=duration)
cache = {}

def adjustTempo(tempo: int):
    global duration, silence

    # y = m * x + b, biiiiitch
    duration = (MAX_DURATION - MIN_DURATION) * tempo / 255 + MIN_DURATION
    silence = AudioSegment.silent(duration=duration)
    print("D: duration set to "+str(duration))

def process_serial_input(s: serial.Serial):
    global subjects

    # we are not doing all that tedhl on the same line. 
    # T[0],E[0],D[0],H[0],L[0]
    # instead: "X[#]\n", where X is a letter ^,
    # '#' is a number (0-4 for Subject manipulation, 0-253 (?)
    # for the tempo). Square brackets are as written, and commands
    # will always be terminated with a newline.
    raw_serial = s.readline()
    print("D: "+str(raw_serial)+"\n")
    out = []
    cmd = str(raw_serial)[2]
    num = int(raw_serial[2:-3])
    print("D: "+str(cmd)+": "+str(num)+"\n")
    
    # ok slayyyy now let's get to it. i kind of wanna be all clever with this
    # but i'm not doing all that. thx python for no switch statement :(
    if cmd == 'T':
        # adjust tempo - need to map it to the right number tho
        adjustTempo(num)
    else:
        if num > len(subjects):
            print("E: Subject out of range!\n")
            return # we have had ENOUGH of that.
        # enable Subject
        if cmd == 'E':
            subjects[num].enable() 
        elif cmd == 'D':
            subjects[num].disable()
        elif cmd == 'H':
            subjects[num].transpose(1)
        elif cmd == 'L':
            subjects[num].transpose(-1)


    
def setupSubjects():
    global subjects

    # WTC 1, Fugue Subject from Ab Major
    melody1 = ['R', 'R', -3, 4, 1, -3, 6, 2, 4, 'R']
    melody2 = ['R', 13, '+', 12, 13, 8, 9, 13, '+', 12, 13, 15, 8, 13, '+', 12, 13, 15, 6, '+', 8, 9, 'R', 8, '+', 6, 4]
    melody3 = [-8, 'R', -8, 'R', -1, 'R', 'R', -3, -4, 1, 'R', -1, -3, -3, '+', -4, -3, 1, -6, -1, 'R', -3, -4, -4, '+', -6, -4, -1]
    melody4 = ['R', 3, 4, -4, -5, 'R', -4, 'R', 'R', -2, '+', -1, 1, -1, '+', -2, -1, 'R']
    melody5 = ['R', 6, 8, 6, 11, 3, 1, 10, '+', 8, 11, '+', 10, 8, '+', 6, 13, 4, 3]

    subject1 = Subject("Ab-1", melody1)
    subject2 = Subject("c-1", melody2)
    subject3 = Subject("Eb-2", melody3)
    subject4 = Subject("g-1", melody4)
    subject5 = Subject("Bb-1", melody5)

    subjects.append(subject1)
    subjects.append(subject2)
    subjects.append(subject3)
    subjects.append(subject4)
    subjects.append(subject5)

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
    setupSubjects()

    # Set up serial port
    ser = setupSerial()
    silence = AudioSegment.silent(duration=duration)
    output = silence

    while True:
        # poll serial port
        while ser.in_waiting: # while could be risky! fuck it up!
            process_serial_input(ser)

        # play the next note for each enabled Subject, maintaining timing
        output = silence
        for s in subjects:
            note = s.play(duration)
            if(note):
                output = output.overlay(note)
                # this ^ throws up a bunch of logs in the terminal, figure out how to silence those? :(
        play(output)
    ser.close()
