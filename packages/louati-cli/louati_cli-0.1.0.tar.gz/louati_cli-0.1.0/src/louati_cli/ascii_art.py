import pyfiglet
from termcolor import colored

def generate_ascii_art(name: str, color: str = "magenta") -> str:
    """
    Generate colored ASCII art text.
    
    Args:
        name: Text to convert to ASCII art
        color: Color for the text
        
    Returns:
        Colored ASCII art string
    """
    fig = pyfiglet.Figlet(font='slant')
    ascii_text = fig.renderText(name)
    
    # Color each line
    colored_lines = []
    for line in ascii_text.split('\n'):
        if line.strip():  # Skip empty lines
            colored_line = colored(line, color, attrs=['bold'])
            colored_lines.append(colored_line)
        else:
            colored_lines.append('')
            
    return '\n'.join(colored_lines)

def show_welcome():
    """Display welcome ASCII art."""
    art = generate_ascii_art("LOUATI MAHDI", "magenta")
    print("\n" + "=" * 50)
    print(art)
    print("=" * 50)
    print(colored("Data Engineer | Problem Solver | Insights Expert", "cyan", attrs=['bold']))
    print(colored("GitHub: https://github.com/mahdi123-tech\n", "yellow"))