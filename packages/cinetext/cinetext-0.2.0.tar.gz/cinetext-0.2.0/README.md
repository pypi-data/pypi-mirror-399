# Cinetext

A Python library for creating cinematic and dynamic text effects in your command-line applications.

This new version includes a more consistent API, smoother animations for multi-line text, and more robust parameter handling.

## Installation

You can install or update to the latest version of `cinetext` using pip:
```bash
pip install --upgrade cinetext
```

## Usage

First, import the functions you want to use from the library:

```python
from cinetext import cinetext_clear, cinetext_type, cinetext_glitch, cinetext_rainbow, cinetext_pulse
```

### Functions

Here is a breakdown of the available functions and their parameters:

*   `cinetext_clear()`
    *   Clears the entire terminal screen and moves the cursor to the top-left corner.

*   `cinetext_type(text, speed=0.04)`
    *   `text` (str): The text you want to display with a typewriter effect.
    *   `speed` (float, optional): The time delay in seconds between each character. Defaults to `0.04`.

*   `cinetext_glitch(text, frames=20, speed=0.08)`
    *   `text` (str): The text you want to display with a glitch effect. Can be multi-line.
    *   `frames` (int, optional): The number of animation frames. Defaults to `20`.
    *   `speed` (float, optional): The time delay in seconds between each frame. Defaults to `0.08`.

*   `cinetext_rainbow(text, frames=50, speed=0.05)`
    *   `text` (str): The text you want to display with a rainbow wave effect. Can be multi-line.
    *   `frames` (int or float, optional): The number of animation frames. Defaults to `50`. If you provide a float (e.g., `0.1`), it will be used as the `speed` and frames will default to 50.
    *   `speed` (float, optional): The time delay in seconds between each frame. Defaults to `0.05`.

*   `cinetext_pulse(text, cycles=3, speed=0.05)`
    *   `text` (str): The text you want to display with a pulsing grayscale effect. Can be multi-line.
    *   `cycles` (int or float, optional): The number of times the text should pulse. Defaults to `3`. If you provide a float, it will be used as the `speed`.
    *   `speed` (float, optional): The time delay in seconds between each frame. Defaults to `0.05`.


### Example

Here is an example demonstrating how to use the functions to create a cinematic sequence.

```python
from cinetext import cinetext_clear, cinetext_type, cinetext_glitch, cinetext_rainbow, cinetext_pulse

def run_intro():
    logo = r"""
     _______  _________ _        _______ _________ _______             _________ 
    (  ____ \ \__   __/( (    /|(  ____ \__   __/(  ____ \   |\     /|\__   __/
    | (    \/    ) (   |  \  ( || (    \/   ) (   | (    \/   ( \   / )   ) (   
    | |          | |   |   \ | || (__       | |   | (__        \ (_) /    | |   
    | |          | |   | (\ \) ||  __)      | |   |  __)        ) _ (     | |   
    | |          | |   | | \   || (         | |   | (          / ( ) \    | |   
    | (____/\ ___) (___| )  \  || (____/\   | |   | (____/\   ( /   \ )   | |   
    (_______/ \_______/|/    )_)(_______/   )_(   (_______/   |/     \|   )_(   
    """
    
    # 1. Clear the screen
    cinetext_clear()
    
    # 2. Show an initializing message
    cinetext_type(">>> INITIALIZING CINETEXT PROTOCOL...", 0.03)
    
    # 3. Animate the logo with a rainbow effect
    # Note: We can pass speed as the second argument directly
    cinetext_rainbow(logo, 0.02) 
    
    # 4. Glitch the logo for a cool effect
    cinetext_glitch(logo, frames=10)
    
    # 5. Pulse the logo
    cinetext_pulse(logo, cycles=1)
    
    print("\n[SYSTEM READY]")

if __name__ == "__main__":
    run_intro()
```