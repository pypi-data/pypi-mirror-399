import sys, time, random, string

def typewriter(text, speed=0.05):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()

def glitch_text(text, duration=10):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    current_list = [random.choice(chars) for _ in text]
    
    for _ in range(duration):
        for i in range(len(text)):
            if current_list[i] != text[i]:
                current_list[i] = random.choice(chars) if random.random() > 0.2 else text[i]
        
        # \r moves the cursor to the start of the line
        sys.stdout.write(f"\r{''.join(current_list)}")
        sys.stdout.flush()
        time.sleep(0.1)
    print() # Move to next line



def pulse_text(text, cycles=3):
    # Grayscale RGB values from dark to light
    shades = [60, 100, 150, 200, 255, 200, 150, 100, 60]
    
    for _ in range(cycles):
        for s in shades:
            # ANSI escape for RGB text: \033[38;2;R;G;Bm
            sys.stdout.write(f"\r\033[38;2;{s};{s};{s}m{text}\033[0m")
            sys.stdout.flush()
            time.sleep(0.05)
    print()


def spinner(duration_seconds, aftermessage):
    symbols = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + duration_seconds
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f"\r{symbols[i % len(symbols)]} Processing data...")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    print("\r", aftermessage)



def rainbow_wave(text, speed=0.1):
    for i in range(50): # Run for 50 frames
        output = ""
        for j, char in enumerate(text):
            # Calculate a color offset based on time (i) and position (j)
            hue = (i + j) % 6
            color = [31, 33, 32, 36, 34, 35][hue] # Red, Yellow, Green, Cyan, Blue, Magenta
            output += f"\033[{color}m{char}"
        
        sys.stdout.write(f"\r{output}\033[0m")
        sys.stdout.flush()
        time.sleep(speed)
    print()

def reset_effect():
    """Resets terminal formatting."""
    sys.stdout.write("\033[0m")
    sys.stdout.flush()
