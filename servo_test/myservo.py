import RPi.GPIO as GPIO
import time
from argparse import ArgumentParser


def main(degree):
    servo_pin = 18
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servo_pin, GPIO.OUT)
    servo = GPIO.PWM(servo_pin, 50)
    servo.start(0.0)
    servo.changeDutyCycle(degree)
    time.sleep(1.0)
    GPIO.cleanup()


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--d]'
    )
    arg_parser.add_argument('-d', '--degree', default=7.0, help='degree')
    options = arg_parser.parse_args()

    main(degree=options.degree)
