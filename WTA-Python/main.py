import random

import pydub.generators
from pydub import AudioSegment
from pydub.playback import play
import serial
import re

def generate_audio_around_freq(freq: int, duration: int, freq_step_lower: int, freq_step: int, range_multi: int = 10) -> AudioSegment:
    output = pydub.generators.Sine(freq).to_audio_segment(duration)
    local_i = freq - freq_step * range_multi
    while local_i < freq + freq_step * range_multi:
        output.overlay(pydub.generators.Sine(local_i).to_audio_segment(duration))
        local_i += random.randrange(freq_step_lower, freq_step)
    return output


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

test: AudioSegment
sig_gen = pydub.generators.Sine(440)
test2 = pydub.generators.Sine(880).to_audio_segment(1000.0)
test = sig_gen.to_audio_segment(1000.0)
test3 = test.overlay(test2)

drum_attack_source = pydub.generators.Sawtooth(175).to_audio_segment(duration=100)
drum_attack = (drum_attack_source + 10).fade(to_gain=-120, start=5, end=100)
drum_attack_source_2 = pydub.generators.Sine(900).to_audio_segment(duration=100)
drum_attack_2 = (drum_attack_source_2 + 10).fade(to_gain=-120, start=5, end=100)
drum_attack_3 = generate_audio_around_freq(200, 100, 1, 5)+20
drum_body_1 = generate_audio_around_freq(6000, 1000, 50, 200)+20
play(drum_attack_3)
# play(drum_attack.overlay(drum_attack_2).overlay(drum_body_1))
# play(drum_attack.overlay(drum_attack_2).overlay(drum_body_1).overlay(drum_attack_3))
# play(test3)
ser = serial.Serial()
ser.baudrate = 9600
ser.port = 'COM5'
ser.timeout = 0.25
ser.open()
print(ser.isOpen())
while True:
    if ser.in_waiting:
        process_serial_input(ser)
ser.close()