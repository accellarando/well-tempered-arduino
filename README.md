# The Well-Tempered Arduino

This is an Arduino and Python project to create sound art based on selected subject themes from The Well-Tempered Clavier by JS Bach.

The user can enable, disable, and transpose up to 5 of the selected melodies at once. These melodies will loop. The tempo is also configurable via a potentiometer.

## Hardware
The hardware consist of 1 enable/disable button, a transpose up button and transpose down button per melody for a total of 15 buttons. One potentiometer to control the tempo and 1 Arduino.

## Arduino Software
The program on the Arduino polls the buttons, digitally debounces them, Then formats and sends that information over serial to the PC program.

## PC software
The PC program reads in a processes serial from the Arduino then modifies and combines the active melodies into a single output that is then played.

## The Goal
The goal was to produce novel results by layering simple repeating sounds together. As we have discussed in class one thing is interesting but many things are many times as interesting. We had hopped to have six melodies but we ran into a limit of how many inputs a single Arduino could support.
