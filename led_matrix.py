#!/usr/bin/env python3
"""
LED Matrix Display Controller
Controls a 3x3 LED matrix to display patterns and images
"""

import RPi.GPIO as GPIO
import time
import threading

class LEDMatrix:
    def __init__(self):
        # GPIO pins for the 3x3 matrix
        self.pins = [
            [18, 19, 20],  # Top row
            [21, 22, 23],  # Middle row
            [24, 25, 26]   # Bottom row
        ]
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Initialize all pins as outputs
        for row in self.pins:
            for pin in row:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)
        
        self.running = False
        self.animation_thread = None
    
    def set_pixel(self, row, col, state):
        """Set a single LED on or off"""
        if 0 <= row < 3 and 0 <= col < 3:
            GPIO.output(self.pins[row][col], GPIO.HIGH if state else GPIO.LOW)
    
    def clear_display(self):
        """Turn off all LEDs"""
        for row in range(3):
            for col in range(3):
                self.set_pixel(row, col, False)
    
    def display_pattern(self, pattern):
        """Display a 3x3 pattern"""
        self.clear_display()
        for row in range(3):
            for col in range(3):
                if row < len(pattern) and col < len(pattern[row]):
                    self.set_pixel(row, col, pattern[row][col])
    
    def display_letter(self, letter):
        """Display letters A-Z"""
        patterns = {
            'A': [
                [0, 1, 0],
                [1, 0, 1],
                [1, 1, 1]
            ],
            'B': [
                [1, 1, 0],
                [1, 1, 0],
                [1, 1, 1]
            ],
            'C': [
                [1, 1, 1],
                [1, 0, 0],
                [1, 1, 1]
            ],
            'H': [
                [1, 0, 1],
                [1, 1, 1],
                [1, 0, 1]
            ],
            'I': [
                [1, 1, 1],
                [0, 1, 0],
                [1, 1, 1]
            ],
            'O': [
                [1, 1, 1],
                [1, 0, 1],
                [1, 1, 1]
            ],
            'X': [
                [1, 0, 1],
                [0, 1, 0],
                [1, 0, 1]
            ],
            'HEART': [
                [1, 0, 1],
                [1, 1, 1],
                [0, 1, 0]
            ],
            'SMILE': [
                [1, 0, 1],
                [0, 0, 0],
                [1, 1, 1]
            ],
            'ARROW': [
                [0, 1, 0],
                [1, 1, 1],
                [0, 1, 0]
            ]
        }
        
        if letter.upper() in patterns:
            self.display_pattern(patterns[letter.upper()])
    
    def blink_all(self, duration=0.5, times=3):
        """Blink all LEDs"""
        for _ in range(times):
            # Turn all on
            for row in range(3):
                for col in range(3):
                    self.set_pixel(row, col, True)
            time.sleep(duration)
            
            # Turn all off
            self.clear_display()
            time.sleep(duration)
    
    def wave_animation(self, delay=0.3):
        """Create a wave effect"""
        patterns = [
            [[1, 0, 0], [0, 0, 0], [0, 0, 0]],
            [[0, 1, 0], [0, 0, 0], [0, 0, 0]],
            [[0, 0, 1], [0, 0, 0], [0, 0, 0]],
            [[0, 0, 0], [0, 0, 1], [0, 0, 0]],
            [[0, 0, 0], [0, 0, 0], [0, 0, 1]],
            [[0, 0, 0], [0, 0, 0], [0, 1, 0]],
            [[0, 0, 0], [0, 0, 0], [1, 0, 0]],
            [[0, 0, 0], [1, 0, 0], [0, 0, 0]]
        ]
        
        for pattern in patterns:
            if not self.running:
                break
            self.display_pattern(pattern)
            time.sleep(delay)
    
    def start_animation(self, animation_type="wave"):
        """Start continuous animation"""
        self.running = True
        
        def animate():
            while self.running:
                if animation_type == "wave":
                    self.wave_animation()
                elif animation_type == "blink":
                    self.blink_all()
                time.sleep(0.1)
        
        self.animation_thread = threading.Thread(target=animate)
        self.animation_thread.daemon = True
        self.animation_thread.start()
    
    def stop_animation(self):
        """Stop animation"""
        self.running = False
        if self.animation_thread:
            self.animation_thread.join()
    
    def cleanup(self):
        """Clean up GPIO"""
        self.stop_animation()
        self.clear_display()
        GPIO.cleanup()

# Example usage
if __name__ == "__main__":
    matrix = LEDMatrix()
    
    try:
        print("LED Matrix Demo Starting...")
        
        # Display letters
        letters = ['H', 'I', 'HEART', 'SMILE']
        for letter in letters:
            print(f"Displaying: {letter}")
            matrix.display_letter(letter)
            time.sleep(2)
        
        # Blink animation
        print("Blinking...")
        matrix.blink_all(times=5)
        
        # Wave animation
        print("Starting wave animation (press Ctrl+C to stop)")
        matrix.start_animation("wave")
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        matrix.cleanup()
        print("Cleanup complete!")
