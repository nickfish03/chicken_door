#!/usr/bin/python3.9

import RPi.GPIO as GPIO
import time
from datetime import datetime
from flask import Flask, render_template, request

# Pins
# Raspberry Pi Zero W, pin notes are for SD card slot facing up and at the top
# 3.3V at L9; GND at L5;
relay_pin_cw = 17 		# signal pin to relay for DC+ (clockwise); L6
relay_pin_ccw = 18      # signal pin to relay for DC- (counter clockwise); R6

# Setup web-page and functions
app = Flask(__name__)

# Default open and close times
motion = 10        # Seconds for motor motion

# Default door_message
door_message = "are you sure?"

def main():

    # GPIO setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(relay_pin_cw, GPIO.OUT)
    GPIO.output(relay_pin_cw, GPIO.LOW)	# relay_pin_cw set as output with initial state of LOW
    GPIO.setup(relay_pin_ccw, GPIO.OUT)
    GPIO.output(relay_pin_ccw, GPIO.LOW)	# relay_pin_ccw set as output with initial state of LOW

    # Start web-server
    app.run(host='0.0.0.0', port=80)

# Open door
def open_door(door_message, motion):

    if door_message == "door is closed" or door_message == "are you sure?":
        GPIO.output(relay_pin_cw, GPIO.HIGH)   # activate the relay, powering motor
        time.sleep(motion)
        GPIO.output(relay_pin_cw, GPIO.LOW)
        door_message = "door is open"
    else:
        door_message = "are you sure?"
    return door_message

# Close door
def close_door(door_message, motion):

    if door_message == "door is open" or door_message == "are you sure?":
        GPIO.output(relay_pin_ccw, GPIO.HIGH)   # activate the relay, powering motor
        time.sleep(motion)
        GPIO.output(relay_pin_ccw, GPIO.LOW)    # deactivate relay
        door_message = "door is closed"
    else:
        door_message = "are you sure?"
    return door_message

def update_shared_variables(new_motion):
    motion = new_motion
    return motion

# Home page
@app.route('/')
def index():
    return render_template('index.html',
                            motion=motion,
                            door_message=door_message)

# Call open_door()
@app.route('/open', methods=['GET', 'POST'])
def open_the_door():
    global door_message, motion
    # Code to open the chicken coop door
    if request.method == 'POST':
        open_door()
        return f'''Door should be open
            <p>Message: {door_message}</p>
            <p><a href="/"><button>Home</button></a></p>'''
    else:
        return 'Use Button on Homepage'

# Call close_door()
@app.route('/close', methods=['GET', 'POST'])
def close_the_door():
    # Code to close the chicken coop door
    global door_message, motion
    if request.method == 'POST':
        close_door()
        return f'''Door should be closed
            <p>Message: {door_message}</p>
            <p><a href="/"><button>Home</button></a></p>'''
    else:
        return 'Use Button on Homepage'

# Update scheduled times with text box input
@app.route('/save', methods=['POST'])
def save_times():
    new_motion = int(request.form['time_motion'])
    update_shared_variables(new_motion)
    return render_template('index.html',
                            motion=motion)

if __name__ == "__main__":
    main()

