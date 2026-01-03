"""
CLI for mcp_arena using Typer.
"""

import sys
import os
import importlib
import inspect
from pathlib import Path
from typing import Optional, List, Dict, Any, Type
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Try to import BaseMCPServer but handle potential circular imports if needed
# (Though usually imports inside functions are safer for CLI tools)

app = typer.Typer(
    name="mcp-arena",
    help="CLI for running MCP servers from mcp_arena presets.",
    add_completion=True,
)
console = Console()

PRESENTS_DIR = Path(__file__).parent / "presents"


def _get_available_presets() -> Dict[str, str]:
    """
    Scans the 'presents' directory to find available server modules.
    Returns a dict of {server_name: module_name}.
    e.g., {'github': 'github', 'slack': 'slack'}
    """
    presets = {}
    if not PRESENTS_DIR.exists():
        return presets

    for file in PRESENTS_DIR.glob("*.py"):
        if file.name.startswith("__") or file.name.startswith("base"):
            continue
        
        module_name = file.stem
        # We assume the server name is the module name (e.g. github -> github)
        presets[module_name] = module_name
    
    return presets


def _load_server_class(module_name: str) -> Optional[Type]:
    """
    Dynamically imports the module and finds the MCPServer class.
    We assume the class is named {CamelCase(module_name)}MCPServer.
    """
    try:
        # Dynamically import the module
        module = importlib.import_module(f"mcp_arena.presents.{module_name}")
        
        # Construct expected class name: github -> GithubMCPServer
        # Simple heuristic: Capitalize first letter + MCPServer
        # But some might be multi-word like "local_operation" -> "LocalOperationMCPServer"
        
        # Better approach: find any class inheriting from BaseMCPServer
        from mcp_arena.mcp.server import BaseMCPServer
        
        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj) 
                and issubclass(obj, BaseMCPServer) 
                and obj is not BaseMCPServer
            ):
                return obj
        
        # Fallback for specific naming if multiple classes exist
        # ...
        
    except ImportError as e:
        console.print(f"[bold red]Error importing module {module_name}: {e}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error loading class from {module_name}: {e}[/bold red]")
        
    return None


@app.command("list")
def list_presets():
    """
    List all available MCP server presets.
    """
    presets = _get_available_presets()
    
    table = Table(title="Available MCP Server Presets")
    table.add_column("Preset Name", style="cyan", no_wrap=True)
    table.add_column("Module", style="green")
    
    for name, module in sorted(presets.items()):
        table.add_row(name, f"mcp_arena.presents.{module}")
        
    console.print(table)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def run(
    ctx: typer.Context,
    mcp_server: str = typer.Option(..., "--mcp-server", "-s", help="Name of the MCP server preset to run (e.g., github)."),
):
    """
    Run an MCP server preset.
    
    Any extra arguments passed (e.g., --token XYZ) will be forwarded 
    to the server's constructor.
    """
    console.print(f"[bold blue]Starting MCP Server Preset:[/bold blue] {mcp_server}")
    
    presets = _get_available_presets()
    if mcp_server not in presets:
        console.print(f"[bold red]Error:[/bold red] Server preset '{mcp_server}' not found.")
        console.print("Run [bold cyan]mcp-arena list[/bold cyan] to see available presets.")
        raise typer.Exit(code=1)
        
    server_class = _load_server_class(presets[mcp_server])
    if not server_class:
        console.print(f"[bold red]Error:[/bold red] Could not find a valid MCPServer class in preset '{mcp_server}'.")
        raise typer.Exit(code=1)
        
    # Parse extra arguments into a dictionary
    # ctx.args is a list like ['--token', '123', '--debug']
    # We need to convert this to kwargs
    kwargs = {}
    i = 0
    args = ctx.args
    while i < len(args):
        arg = args[i]
        if arg.startswith("--"):
            key = arg.lstrip("-").replace("-", "_")  # --auth-token -> auth_token
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                value = args[i + 1]
                i += 2
            else:
                # Flag argument (boolean true)
                value = True
                i += 1
            kwargs[key] = value
        else:
            # Positional arg? Ignore or warn
            console.print(f"[yellow]Warning: Ignoring unknown positional argument '{arg}'[/yellow]")
            i += 1
            
    try:
        console.print(f"Initializing {server_class.__name__} with parameters: {list(kwargs.keys())}")
        server_instance = server_class(**kwargs)
        
        console.print(Panel(f"Running [bold green]{server_class.__name__}[/bold green]...", expand=False))
        server_instance.run()
        
    except TypeError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        console.print("Please check that you provided all required arguments for this server.")
    except Exception as e:
        console.print(f"[bold red]Runtime Error:[/bold red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
