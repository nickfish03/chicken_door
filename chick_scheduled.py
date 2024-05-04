import RPi.GPIO as GPIO
import time
from datetime import datetime
from flask import Flask, render_template, request
import threading

# Pins
# Raspberry Pi Zero W, pin notes are for SD card slot facing up and at the top
# 3.3V at L9; GND at L5;
relay_pin_cw = 17 		# signal pin to relay for DC+ (clockwise); L6
relay_pin_ccw = 18      # signal pin to relay for DC- (counter clockwise); R6

# Setup web-page and functions
app = Flask(__name__)

# Lock to protect open/close time updates
variable_lock = threading.Lock()

# Default open and close times
open_hour = 7     # Default opening hour
open_minute = 0   # Default opening minute
close_hour = 20   # Default closing hour
close_minute = 0  # Default closing minute
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

    # Create thread for scheduled door control
    door_control_thread = threading.Thread(target=check_and_control_door)
    door_control_thread.daemon = True  # The thread will exit when the main program exits
    door_control_thread.start()

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
    global door_message, motion

    if door_message == "door is open" or door_message == "are you sure?":
        GPIO.output(relay_pin_ccw, GPIO.HIGH)   # activate the relay, powering motor
        time.sleep(motion)
        GPIO.output(relay_pin_ccw, GPIO.LOW)    # deactivate relay
        door_message = "door is closed"
    else:
        door_message = "are you sure?"
    return door_message

# Check and open/close the door based on time
def check_and_control_door(door_message, motion):

    while True:
        current_time = datetime.now().time()
        if current_time.hour == open_hour and current_time.minute == open_minute:
            open_door(door_message, motion)
        elif current_time.hour == close_hour and current_time.minute == close_minute:
            close_door(door_message, motion)
        time.sleep(60)  # Check every minute

# Update shared variables safely
def update_shared_variables(new_open_hour, new_open_minute, new_close_hour, new_close_minute, new_motion):

    with variable_lock:
        open_hour = new_open_hour
        open_minute = new_open_minute
        close_hour = new_close_hour
        close_minute = new_close_minute
        motion = new_motion
    return open_hour, open_minute, close_hour, close_minute, motion

# Home page
@app.route('/')
def index():
    return render_template('index.html',
                            open_hour=open_hour,
                            open_minute=open_minute,
                            close_hour=close_hour,
                            close_minute=close_minute,
                            motion=motion,
                            door_message=door_message)

# Call open_door()
@app.route('/open', methods=['GET', 'POST'])
def open_the_door():
    # Code to open the chicken coop door
    global door_message
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
    global door_message
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
    new_open_hour = int(request.form['time_open'].split(':')[0])
    new_open_minute = int(request.form['time_open'].split(':')[1])
    new_close_hour = int(request.form['time_close'].split(':')[0])
    new_close_minute = int(request.form['time_close'].split(':')[1])
    new_motion = int(request.form['time_motion'])
    update_shared_variables(new_open_hour, new_open_minute, new_close_hour, new_close_minute, new_motion)
    return render_template('index.html',
                            open_hour=open_hour,
                            open_minute=open_minute,
                            close_hour=close_hour,
                            close_minute=close_minute,
                            motion=motion)

if __name__ == "__main__":
    main()

