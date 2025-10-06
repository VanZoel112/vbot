"""
VZ ASSISTANT v0.0.0.69
Plugin Loader - Extract plugin info for assistant bot

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import os
import ast
from typing import List, Dict


def load_plugins_info(plugins_dir: str = "plugins") -> List[Dict[str, any]]:
    """
    Load plugin information from plugins directory.

    Args:
        plugins_dir: Path to plugins directory

    Returns:
        List of plugin info dictionaries
    """
    plugins = []

    if not os.path.exists(plugins_dir):
        return plugins

    # Get all .py files
    for filename in sorted(os.listdir(plugins_dir)):
        if not filename.endswith(".py") or filename.startswith("_"):
            continue

        plugin_name = filename[:-3]  # Remove .py
        filepath = os.path.join(plugins_dir, filename)

        # Parse plugin info
        info = parse_plugin_file(filepath, plugin_name)
        if info:
            plugins.append(info)

    return plugins


def parse_plugin_file(filepath: str, plugin_name: str) -> Dict[str, any]:
    """
    Parse plugin file to extract info.

    Args:
        filepath: Path to plugin file
        plugin_name: Plugin name (without .py)

    Returns:
        Dictionary with plugin info
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse AST
        tree = ast.parse(content)
        docstring = ast.get_docstring(tree) or ""

        # Extract info from docstring
        lines = [line.strip() for line in docstring.split("\n") if line.strip()]

        # Get description (first line or line with "Plugin")
        description = ""
        for line in lines:
            if "Plugin" in line or "plugin" in line:
                description = line
                break
        if not description and lines:
            description = lines[0]

        # Extract commands
        commands = []
        seen_commands = set()

        def add_command_line(line: str):
            cleaned = line.strip()
            if cleaned and cleaned not in seen_commands:
                commands.append(cleaned)
                seen_commands.add(cleaned)

        # Collect commands from handler docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if any(_is_events_register_decorator(dec) for dec in node.decorator_list):
                    # Use custom function to get docstring (handles global statements before docstring)
                    handler_doc = _get_function_docstring(node)
                    handler_lines = [ln.strip() for ln in handler_doc.split("\n")]

                    collected = []
                    for ln in handler_lines:
                        stripped = ln.strip()
                        if not stripped:
                            if collected:
                                break
                            continue
                        collected.append(stripped)
                    for collected_line in collected:
                        add_command_line(collected_line)

        # Extract commands from module docstring ("Commands" section)
        in_commands_section = False

        for line in lines:
            if line.lower().startswith("commands"):
                in_commands_section = True
                continue

            if in_commands_section:
                if line.startswith("-") or line.startswith("•"):
                    # Remove bullet point
                    cmd_line = line.lstrip("-•").strip()
                    add_command_line(cmd_line)
                elif line.startswith("."):
                    # Direct command
                    add_command_line(line)
                else:
                    # End of commands section
                    if commands:
                        break

        # Format plugin name for display
        display_name = plugin_name.replace("_", " ").title()

        return {
            "name": plugin_name,
            "display_name": display_name,
            "description": description,
            "commands": commands,
            "emoji": get_plugin_emoji(plugin_name)
        }

    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None


def _get_function_docstring(node):
    """
    Get docstring from function, even if not the first statement.

    This handles cases where global statements or other code
    appears before the docstring.
    """
    if not node.body:
        return ""

    # Look for first string literal in function body (check first 5 statements)
    for stmt in node.body[:5]:
        if isinstance(stmt, ast.Expr):
            # Python 3.7 and earlier use ast.Str
            if hasattr(ast, 'Str') and isinstance(stmt.value, ast.Str):
                return stmt.value.s
            # Python 3.8+ uses ast.Constant
            if isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                return stmt.value.value

    return ""


def _is_events_register_decorator(decorator: ast.AST) -> bool:
    """Return True if decorator targets events.register."""
    target = decorator
    if isinstance(decorator, ast.Call):
        target = decorator.func

    if isinstance(target, ast.Attribute):
        value = target.value
        if isinstance(value, ast.Name):
            return value.id == "events" and target.attr == "register"
    return False


def get_plugin_emoji(plugin_name: str) -> str:
    """
    Get emoji for plugin based on name.

    Args:
        plugin_name: Plugin name

    Returns:
        Emoji string
    """
    emoji_map = {
        "ping": "🏓",
        "alive": "✅",
        "help": "📋",
        "admin": "👨‍💼",
        "broadcast": "📡",
        "group": "👥",
        "info": "ℹ️",
        "settings": "⚙️",
        "approve": "✅",
        "developer": "👨‍💻",
        "payment": "💳",
        "music": "🎵",
        "vc": "🎙",
        "showjson": "📄",
        "github": "🐙"
    }

    return emoji_map.get(plugin_name.lower(), "🔧")


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Split list into chunks.

    Args:
        lst: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
