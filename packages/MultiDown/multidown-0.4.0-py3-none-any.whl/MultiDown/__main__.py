from .webapp import start_server
from rich import print
import time

banner = """[bold cyan]
██████╗ ██╗    ██╗███╗   ██╗██╗     ██████╗ ██████╗ 
██╔══██╗██║    ██║████╗  ██║██║     ██╔══██╗██╔══██╗
██████╔╝██║ █╗ ██║██╔██╗ ██║██║     ██║  ██║██████╔╝
██╔═══╝ ██║███╗██║██║╚██╗██║██║     ██║  ██║██╔═══╝ 
██║     ╚███╔███╔╝██║ ╚████║███████╗██████╔╝██║     
╚═╝      ╚══╝╚══╝ ╚═╝  ╚═══╝╚══════╝╚═════╝ ╚═╝     
[/bold cyan]
"""
author ="""[bold cyan]
AUTHOR:BISMOY GHOSH
Thanks for using
[/bold cyan]
"""
def main():
    print(banner)
    print(author)
    print("[bold green]Launching local web UI...[/bold green]")
    start_server()
    