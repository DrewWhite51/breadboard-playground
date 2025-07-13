#!/usr/bin/env python3
"""
5 LED CLI Controller
Control 5 individual LEDs with chainable commands
"""

import RPi.GPIO as GPIO
import time
import threading
import argparse
import sys
from typing import List, Dict, Optional

class LED5CLI:
    def __init__(self):
        # GPIO pin mapping for 5 LEDs
        self.pins = {
            1: 18, 2: 19, 3: 20, 4: 21, 5: 22
        }
        
        # LED states and timers
        self.led_states = {i: False for i in range(1, 6)}
        self.led_timers = {i: None for i in range(1, 6)}
        self.led_blink_tasks = {i: None for i in range(1, 6)}
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        for led_num, pin in self.pins.items():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        
        print("🚀 5 LED CLI Controller Initialized")
        print("LEDs 1-5 mapped to GPIO pins:", dict(self.pins))
    
    def set_led(self, led_num: int, state: bool):
        """Set individual LED state"""
        if led_num in self.pins:
            GPIO.output(self.pins[led_num], GPIO.HIGH if state else GPIO.LOW)
            self.led_states[led_num] = state
    
    def get_led_state(self, led_num: int) -> bool:
        """Get current LED state"""
        return self.led_states.get(led_num, False)
    
    def stop_led_timer(self, led_num: int):
        """Stop any running timer for LED"""
        if self.led_timers[led_num]:
            self.led_timers[led_num].cancel()
            self.led_timers[led_num] = None
        
        if self.led_blink_tasks[led_num]:
            self.led_blink_tasks[led_num]['stop'] = True
            self.led_blink_tasks[led_num] = None
    
    def on(self, led_nums: List[int]):
        """Turn LEDs on"""
        for led_num in led_nums:
            self.stop_led_timer(led_num)
            self.set_led(led_num, True)
            print(f"💡 LED {led_num} ON")
    
    def off(self, led_nums: List[int]):
        """Turn LEDs off"""
        for led_num in led_nums:
            self.stop_led_timer(led_num)
            self.set_led(led_num, False)
            print(f"⚫ LED {led_num} OFF")
    
    def toggle(self, led_nums: List[int]):
        """Toggle LED states"""
        for led_num in led_nums:
            current_state = self.get_led_state(led_num)
            self.stop_led_timer(led_num)
            self.set_led(led_num, not current_state)
            print(f"🔄 LED {led_num} {'ON' if not current_state else 'OFF'}")
    
    def blink(self, led_nums: List[int], times: int, speed: float = 0.5):
        """Blink LEDs specified number of times"""
        for led_num in led_nums:
            self.stop_led_timer(led_num)
            
            def blink_task(led_id, blink_count, blink_speed):
                task_info = {'stop': False}
                self.led_blink_tasks[led_id] = task_info
                
                for i in range(blink_count):
                    if task_info['stop']:
                        break
                    
                    self.set_led(led_id, True)
                    time.sleep(blink_speed)
                    
                    if task_info['stop']:
                        break
                    
                    self.set_led(led_id, False)
                    time.sleep(blink_speed)
                
                if not task_info['stop']:
                    self.led_blink_tasks[led_id] = None
            
            thread = threading.Thread(target=blink_task, args=(led_num, times, speed))
            thread.daemon = True
            thread.start()
            
            print(f"✨ LED {led_num} blinking {times} times (speed: {speed}s)")
    
    def pulse(self, led_nums: List[int], duration: float = 2.0):
        """Pulse LEDs for specified duration"""
        for led_num in led_nums:
            self.stop_led_timer(led_num)
            
            def pulse_task(led_id, pulse_duration):
                task_info = {'stop': False}
                self.led_blink_tasks[led_id] = task_info
                
                end_time = time.time() + pulse_duration
                while time.time() < end_time and not task_info['stop']:
                    self.set_led(led_id, True)
                    time.sleep(0.05)
                    if task_info['stop']:
                        break
                    self.set_led(led_id, False)
                    time.sleep(0.05)
                
                if not task_info['stop']:
                    self.set_led(led_id, False)
                    self.led_blink_tasks[led_id] = None
            
            thread = threading.Thread(target=pulse_task, args=(led_num, duration))
            thread.daemon = True
            thread.start()
            
            print(f"🌊 LED {led_num} pulsing for {duration}s")
    
    def wave(self, direction: str = "right", speed: float = 0.3, cycles: int = 3):
        """Create wave effect across LEDs"""
        print(f"🌊 Wave effect: {direction} direction, {cycles} cycles")
        
        def wave_task():
            for cycle in range(cycles):
                if direction == "right":
                    sequence = [1, 2, 3, 4, 5]
                elif direction == "left":
                    sequence = [5, 4, 3, 2, 1]
                elif direction == "center_out":
                    sequence = [3, 2, 4, 1, 5]
                elif direction == "center_in":
                    sequence = [1, 5, 2, 4, 3]
                else:
                    sequence = [1, 2, 3, 4, 5]  # default to right
                
                for led_num in sequence:
                    self.clear()
                    time.sleep(0.05)
                    self.set_led(led_num, True)
                    time.sleep(speed)
                
                self.clear()
                time.sleep(speed)
        
        thread = threading.Thread(target=wave_task)
        thread.daemon = True
        thread.start()
    
    def timer(self, led_nums: List[int], seconds: float, action: str = "off"):
        """Set timer to change LED state after delay"""
        for led_num in led_nums:
            self.stop_led_timer(led_num)
            
            def timer_callback(led_id, timer_action):
                if timer_action == "off":
                    self.set_led(led_id, False)
                    print(f"⏰ Timer: LED {led_id} turned OFF")
                elif timer_action == "on":
                    self.set_led(led_id, True)
                    print(f"⏰ Timer: LED {led_id} turned ON")
                elif timer_action == "toggle":
                    current_state = self.get_led_state(led_id)
                    self.set_led(led_id, not current_state)
                    print(f"⏰ Timer: LED {led_id} toggled")
                
                self.led_timers[led_id] = None
            
            timer_obj = threading.Timer(seconds, timer_callback, args=(led_num, action))
            timer_obj.start()
            self.led_timers[led_num] = timer_obj
            
            print(f"⏱️ LED {led_num} timer set: {action} in {seconds}s")
    
    def pattern(self, pattern_name: str):
        """Display predefined patterns"""
        patterns = {
            'all': [1, 2, 3, 4, 5],
            'none': [],
            'ends': [1, 5],
            'middle': [2, 3, 4],
            'center': [3],
            'outer': [1, 2, 4, 5],
            'even': [2, 4],
            'odd': [1, 3, 5],
            'first_three': [1, 2, 3],
            'last_three': [3, 4, 5],
            'alternating1': [1, 3, 5],
            'alternating2': [2, 4],
            'cascade': [1, 2, 3, 4, 5],  # Used with sequence for effects
            'binary1': [1],           # Binary representations
            'binary2': [2],           # 00010
            'binary3': [1, 2],        # 00011
            'binary4': [3],           # 00100
            'binary5': [1, 3],        # 00101
        }
        
        if pattern_name in patterns:
            # Turn off all LEDs first
            self.off(list(range(1, 6)))
            time.sleep(0.1)
            # Turn on pattern LEDs
            if patterns[pattern_name]:
                self.on(patterns[pattern_name])
            print(f"🎨 Pattern '{pattern_name}' displayed")
        else:
            print(f"❌ Unknown pattern: {pattern_name}")
            print("Available patterns:", list(patterns.keys()))
    
    def status(self):
        """Show current status of all LEDs"""
        print("\n📊 LED Status:")
        print("┌─────┬─────┬─────┬─────┬─────┐")
        states = []
        for led_num in range(1, 6):
            state = "🟡" if self.get_led_state(led_num) else "⚫"
            states.append(f"  {state}  ")
        print("│" + "│".join(states) + "│")
        print("│  1  │  2  │  3  │  4  │  5  │")
        print("└─────┴─────┴─────┴─────┴─────┘")
        print("Legend: 🟡 = ON, ⚫ = OFF\n")
    
    def clear(self):
        """Turn off all LEDs and stop all timers"""
        for led_num in range(1, 6):
            self.stop_led_timer(led_num)
        self.off(list(range(1, 6)))
        print("🧹 All LEDs cleared")
    
    def sequence(self, commands: List[str]):
        """Execute a sequence of commands"""
        print(f"🔗 Executing sequence: {' → '.join(commands)}")
        for cmd in commands:
            self.parse_command(cmd.strip())
            time.sleep(0.1)  # Small delay between commands
    
    def loading_bar(self, speed: float = 0.5):
        """Create a loading bar effect"""
        print(f"📊 Loading bar effect (speed: {speed}s)")
        
        def loading_task():
            # Fill up
            self.clear()
            for i in range(1, 6):
                self.set_led(i, True)
                time.sleep(speed)
            
            time.sleep(speed)
            
            # Empty out
            for i in range(1, 6):
                self.set_led(i, False)
                time.sleep(speed)
        
        thread = threading.Thread(target=loading_task)
        thread.daemon = True
        thread.start()
    
    def knight_rider(self, cycles: int = 3, speed: float = 0.2):
        """Knight Rider scanning effect"""
        print(f"🚗 Knight Rider effect: {cycles} cycles")
        
        def knight_task():
            for cycle in range(cycles):
                # Scan right
                for i in range(1, 6):
                    self.clear()
                    time.sleep(0.05)
                    self.set_led(i, True)
                    time.sleep(speed)
                
                # Scan left
                for i in range(5, 0, -1):
                    self.clear()
                    time.sleep(0.05)
                    self.set_led(i, True)
                    time.sleep(speed)
            
            self.clear()
        
        thread = threading.Thread(target=knight_task)
        thread.daemon = True
        thread.start()
    
    def parse_leds(self, led_str: str) -> List[int]:
        """Parse LED numbers from string (e.g., '1,2,3' or '1-3' or 'all')"""
        if led_str.lower() == 'all':
            return list(range(1, 6))
        
        leds = []
        for part in led_str.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                leds.extend(range(start, end + 1))
            else:
                leds.append(int(part))
        
        return [led for led in leds if 1 <= led <= 5]
    
    def parse_command(self, command: str):
        """Parse and execute a single command"""
        parts = command.split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        
        try:
            if cmd == 'on' and len(parts) >= 2:
                leds = self.parse_leds(parts[1])
                self.on(leds)
            
            elif cmd == 'off' and len(parts) >= 2:
                leds = self.parse_leds(parts[1])
                self.off(leds)
            
            elif cmd == 'toggle' and len(parts) >= 2:
                leds = self.parse_leds(parts[1])
                self.toggle(leds)
            
            elif cmd == 'blink' and len(parts) >= 3:
                leds = self.parse_leds(parts[1])
                times = int(parts[2])
                speed = float(parts[3]) if len(parts) > 3 else 0.5
                self.blink(leds, times, speed)
            
            elif cmd == 'pulse' and len(parts) >= 2:
                leds = self.parse_leds(parts[1])
                duration = float(parts[2]) if len(parts) > 2 else 2.0
                self.pulse(leds, duration)
            
            elif cmd == 'wave' and len(parts) >= 1:
                direction = parts[1] if len(parts) > 1 else "right"
                speed = float(parts[2]) if len(parts) > 2 else 0.3
                cycles = int(parts[3]) if len(parts) > 3 else 3
                self.wave(direction, speed, cycles)
            
            elif cmd == 'loading':
                speed = float(parts[1]) if len(parts) > 1 else 0.5
                self.loading_bar(speed)
            
            elif cmd == 'knight':
                cycles = int(parts[1]) if len(parts) > 1 else 3
                speed = float(parts[2]) if len(parts) > 2 else 0.2
                self.knight_rider(cycles, speed)
            
            elif cmd == 'timer' and len(parts) >= 4:
                leds = self.parse_leds(parts[1])
                seconds = float(parts[2])
                action = parts[3]
                self.timer(leds, seconds, action)
            
            elif cmd == 'pattern' and len(parts) >= 2:
                self.pattern(parts[1])
            
            elif cmd == 'sequence' and len(parts) >= 2:
                seq_commands = ' '.join(parts[1:]).split(';')
                self.sequence(seq_commands)
            
            elif cmd == 'status':
                self.status()
            
            elif cmd == 'clear':
                self.clear()
            
            elif cmd == 'help':
                self.show_help()
            
            else:
                print(f"❌ Unknown command: {command}")
                print("Type 'help' for available commands")
        
        except (ValueError, IndexError) as e:
            print(f"❌ Command error: {e}")
            print(f"Usage example: {cmd} <leds> [parameters]")
    
    def show_help(self):
        """Show help information"""
        help_text = """
🔧 5 LED CLI Commands:

BASIC CONTROLS:
  on <leds>                 - Turn LEDs on (e.g., 'on 1,3,5' or 'on all')
  off <leds>                - Turn LEDs off
  toggle <leds>             - Toggle LED states
  clear                     - Turn off all LEDs

ANIMATIONS:
  blink <leds> <times> [speed]    - Blink LEDs (e.g., 'blink 1,5 10 0.3')
  pulse <leds> [duration]         - Pulse LEDs (e.g., 'pulse all 5')
  wave [direction] [speed] [cycles] - Wave effect (right/left/center_out/center_in)
  loading [speed]                 - Loading bar effect
  knight [cycles] [speed]         - Knight Rider scanning effect
  timer <leds> <seconds> <action> - Set timer (e.g., 'timer 1-3 5 off')

PATTERNS:
  pattern <name>           - Display pattern (all, ends, middle, even, odd, etc.)

SEQUENCES:
  sequence <cmd1>; <cmd2>; <cmd3>  - Chain commands with semicolons

UTILITY:
  status                   - Show LED status
  help                     - Show this help

LED SELECTION:
  Individual: 1, 2, 3, 4, 5
  Range: 1-3 (LEDs 1,2,3)
  Multiple: 1,3,5
  All: all

EXAMPLES:
  on 1,5
  blink all 5 0.2
  pattern ends
  wave right 0.3 5
  knight 3 0.1
  loading 0.3
  timer 1-3 10 off
  sequence wave right; knight 2; pattern all
        """
        print(help_text)
    
    def interactive_mode(self):
        """Run interactive CLI mode"""
        print("\n🎮 Interactive Mode - Type commands or 'quit' to exit")
        print("Type 'help' for available commands\n")
        
        try:
            while True:
                command = input("LED> ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                elif command:
                    self.parse_command(command)
        
        except KeyboardInterrupt:
            print("\n")
        
        except EOFError:
            print("\nGoodbye!")
    
    def cleanup(self):
        """Clean up GPIO and stop all timers"""
        for led_num in range(1, 6):
            self.stop_led_timer(led_num)
        
        GPIO.cleanup()
        print("🧹 GPIO cleaned up")

def main():
    parser = argparse.ArgumentParser(description='5 LED CLI Controller')
    parser.add_argument('commands', nargs='*', help='Commands to execute')
    parser.add_argument('-i', '--interactive', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    controller = LED5CLI()
    
    try:
        if args.commands:
            # Execute commands from command line
            command_string = ' '.join(args.commands)
            controller.parse_command(command_string)
        
        if args.interactive or not args.commands:
            # Run interactive mode
            controller.interactive_mode()
    
    except KeyboardInterrupt:
        print("\nStopped by user")
    
    finally:
        controller.cleanup()

if __name__ == "__main__":
    main()