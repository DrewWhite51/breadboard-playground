#!/usr/bin/env python3
"""
Simple LED Test - Just blink one LED
"""

import RPi.GPIO as GPIO
import time

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.OUT)  # GPIO 18 for our test LED

print("Testing LED...")

try:
    # Blink 5 times
    for i in range(5):
        print(f"Blink {i+1}")
        GPIO.output(18, GPIO.HIGH)  # Turn ON
        time.sleep(1)
        GPIO.output(18, GPIO.LOW)   # Turn OFF
        time.sleep(1)
    
    print("Test complete!")
    
except KeyboardInterrupt:
    print("Stopped by user")

finally:
    GPIO.cleanup()  # Always clean up
    print("GPIO cleaned up")
