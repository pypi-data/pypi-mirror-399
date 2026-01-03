import time
from termcolor import colored
from yaspin import yaspin
from yaspin.spinners import Spinners

def thinking_process(message: str, duration: int = 2):
    """
    Display a thinking spinner with custom message.
    
    Args:
        message: Message to display with spinner
        duration: How long to spin (seconds)
    """
    with yaspin(Spinners.dots12, text=colored(message, "yellow")) as spinner:
        time.sleep(duration)
        spinner.ok(" ✅ ")

def display_section(title: str, content: str, color: str = "green"):
    """
    Display a formatted section with title and content.
    
    Args:
        title: Section title
        content: Content to display
        color: Color for title
    """
    print("\n" + colored(f"== {title} ==".center(50), color, attrs=['bold']))
    print(colored(content, "white"))
    print("-" * 50)

def animated_text(text: str, color: str = "cyan", delay: float = 0.05):
    """
    Print text with character-by-character animation.
    
    Args:
        text: Text to animate
        color: Text color
        delay: Delay between characters
    """
    colored_text = colored(text, color)
    for char in colored_text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()