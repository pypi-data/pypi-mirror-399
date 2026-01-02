import sys
import time
import random
import string

def _safe_params(frames, speed):
    if isinstance(frames, float):
        return 50, frames
    return int(frames), float(speed)

def cinetext_clear():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def cinetext_type(text, speed=0.04):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(float(speed))
    print()

def cinetext_glitch(text, frames=20, speed=0.08):
    frames, speed = _safe_params(frames, speed)
    lines = text.splitlines()
    chars = string.ascii_letters + "!@#$%^&*"
    
    sys.stdout.write("\033[?25l\033[s")
    
    for _ in range(frames):
        sys.stdout.write("\033[u\033[J")
        for line in lines:
            glitched = "".join(
                char if random.random() > 0.1 else random.choice(chars) 
                for char in line
            )
            sys.stdout.write(f"{glitched}\n")
        sys.stdout.flush()
        time.sleep(speed)
    
    sys.stdout.write("\033[u\033[J")
    print(text)
    sys.stdout.write("\033[?25h")

def cinetext_rainbow(text, frames=50, speed=0.05):
    frames, speed = _safe_params(frames, speed)
    lines = text.splitlines()
    colors = ["\033[31m", "\033[33m", "\033[32m", "\033[36m", "\033[34m", "\033[35m"]
    
    sys.stdout.write("\033[?25l\033[s") 
    for f in range(frames):
        sys.stdout.write("\033[u\033[J")
        for r, line in enumerate(lines):
            output = ""
            for c, char in enumerate(line):
                color = colors[(f + r + c) % len(colors)]
                output += f"{color}{char}"
            sys.stdout.write(f"{output}\033[0m\n")
        sys.stdout.flush()
        time.sleep(speed)
    sys.stdout.write("\033[?25h")

def cinetext_pulse(text, cycles=3, speed=0.05):
    cycles, speed = _safe_params(cycles, speed)
    lines = text.splitlines()
    shades = list(range(232, 256)) + list(range(254, 232, -1))
    
    sys.stdout.write("\033[?25l\033[s")
    for _ in range(cycles):
        for shade in shades:
            sys.stdout.write("\033[u\033[J")
            for line in lines:
                sys.stdout.write(f"\033[38;5;{shade}m{line}\n")
            sys.stdout.flush()
            time.sleep(speed)
    sys.stdout.write("\033[0m\033[?25h")

def example_cinetext():
    logo = r'''
     _______  _________ _        _______ _________ _______             _________
    (  ____ \ \__   __/( (    /|(  ____ \\__   __/(  ____ \   |\     /|\__   __/
    | (    \/    ) (   |  \  ( || (    \/   ) (   | (    \/   ( \   / )   ) (   
    | |          | |   |   \ | || (___       | |   | (___        \ (_) /    | |   
    | |          | |   | (\ \) ||  __)      | |   |  __)        ) _ (     | |   
    | |          | |   | | \   || (         | |   | (          / ( ) \    | |   
    | (____/\ ___) (___| )  \  || (____/\   | |   | (____/\   ( /   \ )   | |   
    (_______/ \_______/|/    )_)(_______/   )_(   (_______/   |/     \|   )_(   
    '''
    
    cinetext_clear()
    cinetext_type(">>> INITIALIZING CINETEXT PROTOCOL...", 0.03)
    
    cinetext_rainbow(logo, 0.05) 
    
    cinetext_glitch(logo, 10)
    cinetext_pulse(logo, 1)
    
    print("\n[SYSTEM READY]")

