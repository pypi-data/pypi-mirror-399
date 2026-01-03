import click
from .ascii_art import show_welcome
from .utils import thinking_process, display_section, animated_text
from .data import INFO, CONTACT, PROJECTS, EXPERTISE, QUICK_FACTS

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Louati Mahdi CLI - Explore Data Engineering Expertise"""
    if ctx.invoked_subcommand is None:
        show_welcome()
        animated_text("\nWelcome to the interactive CLI about Louati Mahdi!", "cyan")
        animated_text("Type 'louati-cli --help' to see available commands.\n", "yellow")

# =============================================================================
# Commands
# =============================================================================

@cli.command()
def info():
    """Show information about Louati Mahdi"""
    thinking_process("Fetching professional profile...")
    show_welcome()
    display_section("PROFILE", INFO, "green")

@cli.command()
def contact():
    """Display contact information"""
    thinking_process("Retrieving contact details...")
    display_section("CONTACT INFORMATION", CONTACT, "yellow")

@cli.command()
def projects():
    """Show notable projects"""
    thinking_process("Loading project portfolio...")
    display_section("NOTABLE PROJECTS", PROJECTS, "blue")

@cli.command()
def expertise():
    """Show industry problem-solving examples"""
    thinking_process("Preparing industry insights...")
    display_section("INDUSTRY EXPERTISE", EXPERTISE, "magenta")

@cli.command()
def facts():
    """Quick facts about Louati Mahdi"""
    thinking_process("Gathering key facts...")
    display_section("QUICK FACTS", QUICK_FACTS, "cyan")

@cli.command()
def all():
    """Display all information in sequence"""
    thinking_process("Compiling complete profile...", 3)
    
    show_welcome()
    
    display_section("PROFILE", INFO, "green")
    display_section("CONTACT INFORMATION", CONTACT, "yellow")
    display_section("NOTABLE PROJECTS", PROJECTS, "blue")
    display_section("INDUSTRY EXPERTISE", EXPERTISE, "magenta")
    display_section("QUICK FACTS", QUICK_FACTS, "cyan")

# =============================================================================
# Special commands
# =============================================================================

@cli.command()
def explore():
    """Interactive exploration mode"""
    animated_text("\nStarting interactive exploration...\n", "magenta")
    
    while True:
        cmd = click.prompt(
            colored("\nChoose a topic (info/contact/projects/expertise/facts/quit): ", "yellow"),
            type=str
        ).lower()
        
        if cmd == "info":
            info()
        elif cmd == "contact":
            contact()
        elif cmd == "projects":
            projects()
        elif cmd == "expertise":
            expertise()
        elif cmd == "facts":
            facts()
        elif cmd in ["quit", "exit", "q"]:
            animated_text("Thank you for exploring Louati Mahdi's profile!", "green")
            break
        else:
            animated_text("Invalid command. Try again!", "red")

if __name__ == "__main__":
    cli()