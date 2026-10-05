"""
J.A.R.V.I.S. Sci-Fi Terminal Logger & Visual Formatter
"""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

def log_info(msg: str):
    console.print(f"[bold cyan]◆ [JARVIS][/bold cyan] {msg}")

def log_success(msg: str):
    console.print(f"[bold green]✔ [SYSTEM][/bold green] {msg}")

def log_warning(msg: str):
    console.print(f"[bold yellow]▲ [ALERT][/bold yellow] {msg}")

def log_error(msg: str):
    console.print(f"[bold red]✖ [ERROR][/bold red] {msg}")

def log_jarvis_speak(text: str):
    panel = Panel(
        Text(text, style="bold white"),
        title="[bold cyan]⚡ J.A.R.V.I.S. SPEECH[/bold cyan]",
        subtitle="[dim]Audio Output Active[/dim]",
        border_style="cyan"
    )
    console.print(panel)

def print_banner():
    banner_text = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║      ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗                  ║
    ║      ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝                  ║
    ║      ██║███████║██████╔╝██║   ██║██║███████╗                  ║
    ║ ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║                  ║
    ║ ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║                  ║
    ║  ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝                  ║
    ║       Just A Rather Very Intelligent System                   ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(f"[bold cyan]{banner_text}[/bold cyan]")
