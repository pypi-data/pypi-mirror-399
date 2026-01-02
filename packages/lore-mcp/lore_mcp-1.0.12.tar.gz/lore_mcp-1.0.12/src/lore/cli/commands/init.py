"""Init command for Lore - Sets up global hooks and MCP server."""

import json
import os
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Prompt

console = Console()

DASHBOARD_URL = "https://lore-dashboard.jadecon2655.workers.dev"


def get_hooks_config(api_key: str | None = None) -> dict:
    """Get hooks configuration with optional API key env."""
    env_config = {"LORE_API_KEY": api_key} if api_key else {}

    return {
        "PostToolUse": [
            {
                "matcher": "*",
                "hooks": [
                    {
                        "type": "command",
                        "command": "uvx --from lore-mcp python -m lore.hooks.post_tool_use",
                        **({"env": env_config} if env_config else {}),
                    }
                ],
            }
        ],
        "Stop": [
            {
                "matcher": "*",
                "hooks": [
                    {
                        "type": "command",
                        "command": "uvx --from lore-mcp python -m lore.hooks.on_stop",
                        **({"env": env_config} if env_config else {}),
                    }
                ],
            }
        ],
    }


def get_mcp_server_config(api_key: str | None = None) -> dict:
    """Get MCP server configuration."""
    config = {
        "command": "uvx",
        "args": ["lore-mcp"],
    }
    if api_key:
        config["env"] = {"LORE_API_KEY": api_key}
    return config


def get_claude_settings_path() -> Path:
    """Get path to Claude Code global settings file."""
    return Path.home() / ".claude" / "settings.json"


def get_project_local_settings_path() -> Path:
    """Get path to project-local Claude Code settings file."""
    return Path.cwd() / ".claude" / "settings.local.json"


def get_claude_config_path() -> Path:
    """Get path to Claude Code config file (.claude.json)."""
    return Path.home() / ".claude.json"


def load_json_file(path: Path) -> dict:
    """Load JSON file or return empty dict."""
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_json_file(path: Path, data: dict) -> None:
    """Save JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def setup_mcp_server(api_key: str | None = None, force: bool = False) -> bool:
    """Add Lore MCP server to Claude config.

    Returns:
        True if server was added/updated, False if already configured.
    """
    config_path = get_claude_config_path()
    config = load_json_file(config_path)

    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Check if already configured (and not forcing)
    if "lore" in config["mcpServers"] and not force:
        existing = config["mcpServers"]["lore"]
        existing_key = existing.get("env", {}).get("LORE_API_KEY")
        if existing_key and (not api_key or existing_key == api_key):
            return False

    # Add/update MCP server config
    config["mcpServers"]["lore"] = get_mcp_server_config(api_key)
    save_json_file(config_path, config)
    return True


def setup_local_hooks(api_key: str | None = None, force: bool = False) -> bool:
    """Add Lore hooks to project-local Claude settings.

    Returns:
        True if hooks were added/updated, False if already configured.
    """
    settings_path = get_project_local_settings_path()
    settings = load_json_file(settings_path)

    # Check if hooks already exist
    existing_hooks = settings.get("hooks", {})

    # Check if Lore hooks are already configured
    lore_configured = False
    has_env = False

    for hook_type in ["PostToolUse", "Stop"]:
        for hook_config in existing_hooks.get(hook_type, []):
            for hook in hook_config.get("hooks", []):
                if "lore" in hook.get("command", "").lower():
                    lore_configured = True
                    if hook.get("env", {}).get("LORE_API_KEY"):
                        has_env = True
                    break

    # If already configured with env and not forcing, skip
    if lore_configured and has_env and not force:
        return False

    # Remove existing lore hooks if forcing or updating
    if lore_configured:
        for hook_type in ["PostToolUse", "Stop"]:
            if hook_type in settings.get("hooks", {}):
                settings["hooks"][hook_type] = [
                    hc for hc in settings["hooks"][hook_type]
                    if not any("lore" in h.get("command", "").lower()
                              for h in hc.get("hooks", []))
                ]

    # Add hooks with API key env
    hooks_config = get_hooks_config(api_key)

    if "hooks" not in settings:
        settings["hooks"] = {}

    for hook_type, hook_configs in hooks_config.items():
        if hook_type not in settings["hooks"]:
            settings["hooks"][hook_type] = []
        settings["hooks"][hook_type].extend(hook_configs)

    save_json_file(settings_path, settings)
    return True


def get_existing_api_key() -> str | None:
    """Get existing API key from environment or config."""
    # Check environment first
    api_key = os.environ.get("LORE_API_KEY")
    if api_key:
        return api_key

    # Check .claude.json MCP server config
    config = load_json_file(get_claude_config_path())
    return config.get("mcpServers", {}).get("lore", {}).get("env", {}).get("LORE_API_KEY")


def init_command(
    hooks: bool = typer.Option(True, "--hooks/--no-hooks", help="Set up global Claude hooks"),
    mcp: bool = typer.Option(True, "--mcp/--no-mcp", help="Set up MCP server in Claude config"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force re-setup even if already configured"
    ),
    api_key: str | None = typer.Option(
        None, "--api-key", "-k", help="Lore API key (will prompt if not provided)"
    ),
) -> None:
    """Initialize Lore for your system.

    Sets up global Claude Code hooks and MCP server for automatic context capture.
    """
    console.print("\n[bold blue]🔮 Lore MCP Setup[/bold blue]\n")

    # Get API key - check existing, env, option, or prompt
    existing_key = get_existing_api_key()

    if api_key:
        # User provided via --api-key
        pass
    elif existing_key:
        api_key = existing_key
        console.print(f"[green]✓[/green] Using existing API key: {api_key[:12]}...")
    else:
        # Prompt for API key
        console.print(f"[yellow]![/yellow] API key not found.")
        console.print(f"  Get your key at: [link]{DASHBOARD_URL}/api-keys[/link]\n")
        api_key = Prompt.ask("  Enter your API key (or press Enter to skip)")
        if not api_key:
            console.print("[dim]  Skipping API key setup...[/dim]\n")

    # Set up MCP server
    if mcp:
        if setup_mcp_server(api_key, force):
            console.print("[green]✓[/green] MCP server configured")
            console.print("  [dim]Location: ~/.claude.json[/dim]")
        else:
            console.print("[green]✓[/green] MCP server already configured")

    # Set up hooks (project-local)
    if hooks:
        if setup_local_hooks(api_key, force):
            console.print("[green]✓[/green] Project hooks configured")
            console.print("  [dim]Location: .claude/settings.local.json[/dim]")
        else:
            console.print("[green]✓[/green] Hooks already configured for this project")

    if not hooks:
        console.print("[dim]○[/dim] Hooks setup skipped (--no-hooks)")
    if not mcp:
        console.print("[dim]○[/dim] MCP server setup skipped (--no-mcp)")

    console.print("\n[bold green]Lore is ready![/bold green]")
    console.print("\nNext steps:")
    console.print("  1. [bold]Restart Claude Code[/bold] to load the MCP server")
    console.print("  2. Context will be captured in this project")
    console.print(f"  3. View at: [link]{DASHBOARD_URL}[/link]")
    console.print("\n[dim]Run 'lore init' in other projects to enable context capture there.[/dim]")
    console.print()
