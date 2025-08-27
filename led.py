#!/usr/bin/env python3
from time import sleep
from random import randrange as rand
from threading import Thread
import sys
import argparse

# todo: create a device finder
devpath = '/dev/hidraw2'

colors = {
    'red': 0x01,
    'green': 0x02,
    'blue': 0x03,
    'cyan': 0x06,
    'magenta': 0x05,
    'yellow': 0x04,
    'black': 0x08,
    'white': 0x07
}

chsum = lambda b0, b1, b3: (21 * b0**2 + 19 * b1 - 3 * b3) % 255

def bg(f, *args):
    t = Thread(target=f, args=args)
    t.start()

def turn_on(color='white', delay=0.0):
    sleep(delay)
    cmd = bytearray.fromhex('ff' * 64)
    cmd[0] = 0x11
    cmd[1] = colors[color]
    cmd[3] = rand(255)
    cmd[2] = chsum(cmd[0], cmd[1], cmd[3])

    try:
        with open(devpath, 'wb') as device:
            device.write(cmd)
    except BrokenPipeError as e:
        print(f"BrokenPipeError: {e}. Check if the device is connected and ready.")
    except Exception as e:
        print(f"Error writing to device: {e}")

def turn_off(delay=0.0):
    turn_on('black', delay)

def blink(color, count=1, delay=0.2):
    for i in range(count):
        print(f"Blinking {color} ({i+1}/{count})")
        turn_on(color, delay)
        turn_off(delay)
    turn_off()

def gay():
    print("Running rainbow sequence")
    for c in ['red', 'green', 'blue', 'cyan', 'magenta', 'yellow']:
        turn_on(c, 0.1)
    turn_off(0.2)

def list_colors():
    print("Available colors:")
    for color in colors.keys():
        print(f"  - {color}")

def main():
    parser = argparse.ArgumentParser(
        description='LED Controller - Control your LED device',
        epilog='Example: ./led.py --blink red --count 5 --delay 0.5'
    )
    
    # Main action arguments
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument('--on', metavar='COLOR', help='Turn LED on with specified color')
    action_group.add_argument('--off', action='store_true', help='Turn LED off')
    action_group.add_argument('--blink', metavar='COLOR', help='Blink LED with specified color')
    action_group.add_argument('--gay', action='store_true', help='Run rainbow sequence')
    action_group.add_argument('--list-colors', action='store_true', help='List available colors')
    
    # Optional arguments
    parser.add_argument('--count', type=int, default=1, help='Number of blinks (default: 1)')
    parser.add_argument('--delay', type=float, default=0.2, help='Delay between actions in seconds (default: 0.2)')
    parser.add_argument('--background', action='store_true', help='Run command in background thread')
    
    args = parser.parse_args()
    
    if args.list_colors:
        list_colors()
        return
    
    # Validate color arguments
    if (args.on or args.blink) and args.on not in colors and args.blink not in colors:
        print(f"Error: Invalid color. Available colors: {', '.join(colors.keys())}")
        sys.exit(1)
    
    def execute_command():
        if args.on:
            print(f"Turning LED on with {args.on} color")
            turn_on(args.on)
        elif args.off:
            print("Turning LED off")
            turn_off()
        elif args.blink:
            print(f"Blinking LED {args.count} times with {args.blink} color")
            blink(args.blink, args.count, args.delay)
        elif args.gay:
            gay()
    
    if args.background:
        print("Running command in background...")
        bg(execute_command)
    else:
        execute_command()

if __name__ == '__main__':
    main()
