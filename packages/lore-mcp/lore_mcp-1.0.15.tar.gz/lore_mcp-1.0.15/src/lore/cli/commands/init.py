"""Init command for Lore - Sets up global hooks and MCP server."""

import json
import os
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Prompt

console = Console()

DASHBOARD_URL = "https://lore-dashboard.jadecon2655.workers.dev"

MCP_LORE_DOC = """# Lore MCP Server

**Purpose**: Version control for AI coding context.
Captures intent, decisions, and assumptions behind code changes.

## Triggers
- After completing coding tasks or features
- When making architectural decisions
- Before/after significant code changes
- When context needs to be preserved for future sessions
- Debugging sessions where reasoning should be recorded

## Choose When
- **For context preservation**: Capture the "why" behind code, not just the "what"
- **For team collaboration**: Share coding context with team members working on same project
- **For code archaeology**: Find the AI context that led to specific code changes
- **For session continuity**: Maintain context across Claude Code sessions
- **Not for**: Version control of code itself (use git), documentation generation

## Core Tools
- **lore_commit**: Save context with intent, decisions, assumptions, and alternatives
- **lore_blame**: Find AI context for a specific file or line
- **lore_search**: Search through context commits by query
- **lore_status**: Check connection status, plan, team, and projects
- **lore_init**: Initialize Lore hooks in a project

## Works Best With
- **Git**: Lore links context commits to git commits for traceability
- **Claude Code Hooks**: Automatic context capture via PostToolUse and Stop hooks
- **Team workflows**: Share context across team members via cloud sync

## Examples
```
# After implementing a feature
lore_commit(intent="Implement user authentication with JWT",
            decision="Chose JWT over sessions for stateless API",
            assumptions=["API will be horizontally scaled"])

# Find context for code
lore_blame(file_path="src/auth/jwt.py", line_number=42)

# Search for past decisions
lore_search(query="authentication")

# Check status and projects
lore_status()
```

## Dashboard
View and manage your context at: https://lore-dashboard.jadecon2655.workers.dev
"""


def _create_hook_entry(module: str, api_key: str | None = None) -> dict:
    """Create a single hook entry with optional API key env."""
    hook: dict = {
        "type": "command",
        "command": f"uvx --from lore-mcp python -m lore.hooks.{module}",
    }
    if api_key:
        hook["env"] = {"LORE_API_KEY": api_key}
    return hook


def get_hooks_config(api_key: str | None = None) -> dict:
    """Get hooks configuration with optional API key env."""
    return {
        "PostToolUse": [{"matcher": "*", "hooks": [_create_hook_entry("post_tool_use", api_key)]}],
        "Stop": [{"matcher": "*", "hooks": [_create_hook_entry("on_stop", api_key)]}],
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


def get_mcp_doc_path() -> Path:
    """Get path to MCP_Lore.md documentation file."""
    return Path.home() / ".claude" / "MCP_Lore.md"


def get_claude_md_path() -> Path:
    """Get path to CLAUDE.md file."""
    return Path.home() / ".claude" / "CLAUDE.md"


def setup_claude_md_import(force: bool = False) -> bool:
    """Add @MCP_Lore.md import to CLAUDE.md under MCP Documentation section.

    Returns:
        True if import was added, False if already exists or file not found.
    """
    claude_md_path = get_claude_md_path()

    if not claude_md_path.exists():
        return False

    try:
        content = claude_md_path.read_text(encoding="utf-8")
    except OSError:
        return False

    # Check if already imported
    if "@MCP_Lore.md" in content:
        return False

    # Find MCP Documentation section and add import
    lines = content.split("\n")
    new_lines = []
    mcp_section_found = False
    import_added = False

    for i, line in enumerate(lines):
        new_lines.append(line)

        # Found MCP Documentation section header
        if line.strip() == "# MCP Documentation":
            mcp_section_found = True
            continue

        # In MCP section, find last @MCP_ import line
        if mcp_section_found and not import_added:
            # Check if next line is empty or not an @MCP_ import
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            if line.startswith("@MCP_") and (not next_line.startswith("@MCP_")):
                new_lines.append("@MCP_Lore.md")
                import_added = True

    if import_added:
        claude_md_path.write_text("\n".join(new_lines), encoding="utf-8")
        return True

    return False


def setup_mcp_documentation(force: bool = False) -> bool:
    """Create MCP_Lore.md documentation file in ~/.claude/.

    Returns:
        True if file was created/updated, False if already exists.
    """
    doc_path = get_mcp_doc_path()

    # Check if already exists (and not forcing)
    if doc_path.exists() and not force:
        return False

    # Create directory if needed
    doc_path.parent.mkdir(parents=True, exist_ok=True)

    # Write documentation
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(MCP_LORE_DOC)

    return True


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
                    hc
                    for hc in settings["hooks"][hook_type]
                    if not any("lore" in h.get("command", "").lower() for h in hc.get("hooks", []))
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
        console.print(f"[green]✓[/green] Using existing API key: ...{api_key[-4:]}")
    else:
        # Prompt for API key
        console.print("[yellow]![/yellow] API key not found.")
        console.print(f"  Get your key at: [link]{DASHBOARD_URL}/api-keys[/link]\n")
        api_key = Prompt.ask("  Enter your API key (or press Enter to skip)", password=True)
        if not api_key:
            console.print("[dim]  Skipping API key setup...[/dim]\n")

    # Set up MCP server
    if mcp:
        if setup_mcp_server(api_key, force):
            console.print("[green]✓[/green] MCP server configured")
            console.print("  [dim]Location: ~/.claude.json[/dim]")
        else:
            console.print("[green]✓[/green] MCP server already configured")

    # Set up MCP documentation
    if setup_mcp_documentation(force):
        console.print("[green]✓[/green] MCP documentation created")
        console.print("  [dim]Location: ~/.claude/MCP_Lore.md[/dim]")
    else:
        console.print("[green]✓[/green] MCP documentation already exists")

    # Add import to CLAUDE.md (SuperClaude style)
    if setup_claude_md_import(force):
        console.print("[green]✓[/green] Added @MCP_Lore.md import to CLAUDE.md")
    else:
        claude_md = get_claude_md_path()
        if claude_md.exists() and "@MCP_Lore.md" in claude_md.read_text(encoding="utf-8"):
            console.print("[green]✓[/green] CLAUDE.md import already configured")
        # If CLAUDE.md doesn't exist, silently skip (not all users have SuperClaude)

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
