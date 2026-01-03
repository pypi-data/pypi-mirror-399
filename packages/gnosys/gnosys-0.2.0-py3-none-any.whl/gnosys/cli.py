"""GNO.SYS CLI - Compound Intelligence Ecosystem Configuration"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from dotenv import dotenv_values
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def get_template_path(filename: str) -> Path:
    """Get path to template file in package"""
    return Path(__file__).parent / "templates" / filename


def get_config_dir() -> Path:
    """Get Strata config directory"""
    return Path.home() / ".config" / "strata"


def get_gnosys_dir() -> Path:
    """Get GNO.SYS config directory"""
    return Path.home() / ".gnosys"


def init_config():
    """Initialize configuration files"""
    console.print("\n[bold cyan]🌏 Initializing GNO.SYS Configuration[/bold cyan]\n")

    gnosys_dir = get_gnosys_dir()
    gnosys_dir.mkdir(parents=True, exist_ok=True)

    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)

    # Copy .env.example
    env_example = gnosys_dir / ".env.example"
    shutil.copy(get_template_path(".env.example"), env_example)
    console.print(f"✅ Created: {env_example}")

    # Copy servers.json.template
    servers_template = config_dir / "servers.json.template"
    shutil.copy(get_template_path("servers.json.template"), servers_template)
    console.print(f"✅ Created: {servers_template}")

    console.print(f"\n[bold green]✨ Next steps:[/bold green]")
    console.print(f"1. Copy and fill out environment variables:")
    console.print(f"   [cyan]cp {env_example} {gnosys_dir / '.env'}[/cyan]")
    console.print(f"   [cyan]nano {gnosys_dir / '.env'}[/cyan]")
    console.print(f"\n2. Configure Strata MCPs:")
    console.print(f"   [cyan]gnosys configure-strata[/cyan]")
    console.print(f"\n3. Restart Claude Code to load MCPs\n")


def check_neo4j_connection(uri: str, user: str, password: str) -> bool:
    """Check if Neo4j is reachable"""
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            session.run("RETURN 1")
        driver.close()
        return True
    except ImportError:
        console.print("[yellow]⚠️  neo4j package not installed, skipping connection check[/yellow]")
        return True  # Don't fail if optional
    except Exception as e:
        console.print(f"[red]❌ Neo4j connection failed: {e}[/red]")
        console.print("\n[yellow]💡 To start Neo4j:[/yellow]")
        console.print("   [cyan]docker run -d -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest[/cyan]")
        return False


def configure_strata():
    """Configure Strata MCPs from .env file"""
    console.print("\n[bold cyan]⚙️  Configuring Strata MCPs[/bold cyan]\n")

    # Load .env
    env_path = get_gnosys_dir() / ".env"
    if not env_path.exists():
        console.print(f"[red]❌ Error: {env_path} not found[/red]")
        console.print(f"Run: [cyan]gnosys init[/cyan] first")
        sys.exit(1)

    env_vars = dotenv_values(env_path)

    # Validate required vars
    required_vars = [
        "GITHUB_PAT", "REPO_URL", "NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD",
        "OPENAI_API_KEY", "HEAVEN_DATA_DIR", "LLM_INTELLIGENCE_DIR",
        "CHROMA_PERSIST_DIR", "GIINT_TREEKANBAN_BOARD"
    ]

    missing = [var for var in required_vars if not env_vars.get(var)]
    if missing:
        console.print(f"[red]❌ Missing required environment variables:[/red]")
        for var in missing:
            console.print(f"   • {var}")
        console.print(f"\nEdit: [cyan]{env_path}[/cyan]")
        sys.exit(1)

    # Check Neo4j connection
    console.print("🔍 Checking Neo4j connection...")
    if not check_neo4j_connection(
        env_vars["NEO4J_URI"],
        env_vars["NEO4J_USER"],
        env_vars["NEO4J_PASSWORD"]
    ):
        console.print("\n[yellow]⚠️  Neo4j check failed. Continue anyway? (y/n)[/yellow] ", end="")
        if input().lower() != 'y':
            sys.exit(1)
    else:
        console.print("[green]✅ Neo4j connection successful[/green]")

    # Load template
    template_path = get_config_dir() / "servers.json.template"
    if not template_path.exists():
        console.print(f"[red]❌ Template not found: {template_path}[/red]")
        console.print(f"Run: [cyan]gnosys init[/cyan] first")
        sys.exit(1)

    with open(template_path) as f:
        template_content = f.read()

    # Replace all {{VAR}} with values from .env
    configured_content = template_content
    for key, value in env_vars.items():
        placeholder = f"{{{{{key}}}}}"
        if placeholder in configured_content:
            configured_content = configured_content.replace(placeholder, value or "")

    # Write to servers.json
    output_path = get_config_dir() / "servers.json"
    with open(output_path, 'w') as f:
        # Validate JSON before writing
        json.loads(configured_content)  # Will raise if invalid
        f.write(configured_content)

    console.print(f"\n[bold green]✅ Configured: {output_path}[/bold green]")
    console.print(f"\n[yellow]⚠️  Restart Claude Code to load MCPs[/yellow]\n")


def show_status():
    """Show configuration status"""
    console.print("\n[bold cyan]📊 GNO.SYS Status[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Location")

    # Check .env
    env_path = get_gnosys_dir() / ".env"
    env_status = "✅ Configured" if env_path.exists() else "❌ Missing"
    table.add_row(".env", env_status, str(env_path))

    # Check servers.json
    servers_path = get_config_dir() / "servers.json"
    servers_status = "✅ Configured" if servers_path.exists() else "❌ Missing"
    table.add_row("Strata Config", servers_status, str(servers_path))

    # Check Neo4j if env exists
    if env_path.exists():
        env_vars = dotenv_values(env_path)
        neo4j_ok = check_neo4j_connection(
            env_vars.get("NEO4J_URI", ""),
            env_vars.get("NEO4J_USER", ""),
            env_vars.get("NEO4J_PASSWORD", "")
        )
        neo4j_status = "✅ Connected" if neo4j_ok else "❌ Unreachable"
        table.add_row("Neo4j", neo4j_status, env_vars.get("NEO4J_URI", ""))

    console.print(table)
    console.print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="GNO.SYS - Compound Intelligence Ecosystem Configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gnosys init              Initialize configuration files
  gnosys configure-strata  Configure Strata MCPs from .env
  gnosys status            Show configuration status
        """
    )

    parser.add_argument(
        "command",
        choices=["init", "configure-strata", "status"],
        help="Command to run"
    )

    args = parser.parse_args()

    # Show header
    console.print(Panel.fit(
        "[bold cyan]☀️🌏💗🌐[/bold cyan]\n"
        "[bold]GNO.SYS[/bold]\n"
        "Compound Intelligence Ecosystem",
        border_style="cyan"
    ))

    if args.command == "init":
        init_config()
    elif args.command == "configure-strata":
        configure_strata()
    elif args.command == "status":
        show_status()


if __name__ == "__main__":
    main()
