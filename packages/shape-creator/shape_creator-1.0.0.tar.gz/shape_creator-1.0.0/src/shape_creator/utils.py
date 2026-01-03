import os
import sys

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_valid_input(prompt, min_val, max_val):
    while True:
        try:
            val = int(input(prompt))
            if min_val <= val <= max_val:
                return val
            print(f"Please enter a value between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid number.")
