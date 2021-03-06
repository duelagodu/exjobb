import board
import signal
import sys
import time
import RPi.GPIO as IO

light = 23

IO.setup(light, IO.OUT)

def signal_handler(sig, frame): 
    IO.cleanup()
    sys.exit(0)

def set_light(state):
    if state:
        IO.output(light, IO.HIGH)
    else:
        IO.output(light, IO.LOW)

# Lamp flash
def flash_light(state):
    set_light(not state)
    time.sleep(1)
    set_light(state)

