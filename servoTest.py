from BreakfastSerial import Arduino, Servo
from time import sleep

board = Arduino()

# servo_red: GPIO 3
# servo_blue: GPIO 5
# servo_green: GPIO 6

servo = Servo(board,3)

# Safe init
servo.set_position(80)

while(True):
	servoTestVal = raw_input("Enter an int: ")
	servo.set_position(servoTestVal)
	sleep(1)

# The safe ranges:
# servo_red (0, 175)	 CCW_inc
# servo_blue (15, 95)	 (Up,Down)
# servo_green (50, 105)  (Down,Up)

# Blue servo is overloaded ... too heavy!


# servo.set_position(180)
# sleep(2)
# servo.move(-180)
# sleep(2)
# servo.center()
# sleep(2)
# servo.reset()