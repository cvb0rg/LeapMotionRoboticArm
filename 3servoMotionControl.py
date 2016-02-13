################################################################################
# Adapted from sample.py
# Control 3 servos, actuating a robotic arm:
# Servo_red is controlling the rotation around the z-axis
# Servo_blue is mounted at the base of the arm.
# Servo_green is mounted at the mid-section of the arm.
# A combination of 2 & 3 moves the arm up and down in a plane containing the z-axis
################################################################################

# Force float division on integers
# from __future__ import division

import os, sys, inspect, thread, time
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = 'lib/'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))


import Leap, sys
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
from BreakfastSerial import Arduino, Servo, Led
from time import sleep




board = Arduino()

# # Blink some Leds TEST
# redLed = Led(board, 10)
# greenLed = Led(board, 11)

# for i in range(10):
#     redLed.on()
#     sleep(1)
#     redLed.off()

servo_red = Servo(board,3)
servo_blue = Servo(board,5)
servo_green = Servo(board,6)

def mapVal(inputPos, in_min, in_max, out_min, out_max):
    """ This function will linearly scale an incoming value 
        belonging to a certain range (in_max - in_min) to a new 
        value in the out range (out_max - out_min). """
    
 
    scale = ((out_max - out_min) / (in_max - in_min))
    return float(((inputPos - in_min) * scale) + out_min)

def constrain(inputVal, lower_limit, upper_limit):
    """ Clips the input Value in the range 
        (upper_limit - lower_limit)"""
    
    if (inputVal < lower_limit):
        return lower_limit
    elif (inputVal > upper_limit):
        return upper_limit
    else:
        return inputVal


class SampleListener(Leap.Listener):
    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
              frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))

        if not frame.hands.is_empty:
            # Get the first hand
            hand = frame.hands[0]

            # Check if the hand has any fingers
            fingers = hand.fingers
            if not fingers.is_empty:
                # Calculate the hand's average finger tip position
                avg_pos = Leap.Vector()
                for finger in fingers:
                    avg_pos += finger.tip_position
                avg_pos /= len(fingers)
                # print "Hand has %d fingers, average finger tip position: %s" % (
                #       len(fingers), avg_pos)
            print avg_pos

            # To Arduino
            redVal = constrain(mapVal(avg_pos[0], -150., 150., 0., 180.), 0., 175.)
            servo_red.set_position(redVal)

            blueVal = constrain(mapVal(avg_pos[2], -100., 120., 0., 180.), 15., 95.)
            servo_blue.set_position(blueVal)

            greenVal = constrain(mapVal(avg_pos[1], 50., 250., 0., 180.), 50., 105.)
            servo_green.set_position(greenVal)

            print "redVal: %d, blueVal: %d, greenVal: %d" % (redVal, blueVal, greenVal)

            # Get the hand's sphere radius and palm position
            # print "Hand sphere radius: %f mm, palm position: %s" % (
            #       hand.sphere_radius, hand.palm_position)

            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction

            # Calculate the hand's pitch, roll, and yaw angles
            # print "Hand pitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (
            #     direction.pitch * Leap.RAD_TO_DEG,
            #     normal.roll * Leap.RAD_TO_DEG,
            #     direction.yaw * Leap.RAD_TO_DEG)

            # Gestures
            for gesture in frame.gestures():
                if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                    circle = CircleGesture(gesture)

                    # Determine clock direction using the angle between the pointable and the circle normal
                    if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/4:
                        clockwiseness = "clockwise"
                    else:
                        clockwiseness = "counterclockwise"

                    # Calculate the angle swept since the last frame
                    swept_angle = 0
                    if circle.state != Leap.Gesture.STATE_START:
                        previous_update = CircleGesture(controller.frame(1).gesture(circle.id))
                        swept_angle =  (circle.progress - previous_update.progress) * 2 * Leap.PI

                    print "Circle id: %d, %s, progress: %f, radius: %f, angle: %f degrees, %s" % (
                            gesture.id, self.state_string(gesture.state),
                            circle.progress, circle.radius, swept_angle * Leap.RAD_TO_DEG, clockwiseness)

                if gesture.type == Leap.Gesture.TYPE_SWIPE:
                    swipe = SwipeGesture(gesture)
                    print "Swipe id: %d, state: %s, position: %s, direction: %s, speed: %f" % (
                            gesture.id, self.state_string(gesture.state),
                            swipe.position, swipe.direction, swipe.speed)

                if gesture.type == Leap.Gesture.TYPE_KEY_TAP:
                    keytap = KeyTapGesture(gesture)
                    print "Key Tap id: %d, %s, position: %s, direction: %s" % (
                            gesture.id, self.state_string(gesture.state),
                            keytap.position, keytap.direction )

                if gesture.type == Leap.Gesture.TYPE_SCREEN_TAP:
                    screentap = ScreenTapGesture(gesture)
                    print "Screen Tap id: %d, %s, position: %s, direction: %s" % (
                            gesture.id, self.state_string(gesture.state),
                            screentap.position, screentap.direction )

        if not (frame.hands.is_empty and frame.gestures().is_empty):
            print ""

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    sys.stdin.readline()

    # Remove the sample listener when done
    controller.remove_listener(listener)


if __name__ == "__main__":
    main()

