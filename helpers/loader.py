"""
VZ ASSISTANT v0.0.0.69
Plugin Loader with Event Handler Registration

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import os
import sys
import importlib
from telethon import events

# Global registry for all event handlers
_event_handlers = []

def register_handler(handler):
    """Register an event handler globally."""
    _event_handlers.append(handler)
    return handler

def get_all_handlers():
    """Get all registered event handlers."""
    return _event_handlers

def load_plugins(client):
    """
    Load all plugins from plugins directory and register their handlers to client.

    Args:
        client: The Telethon client or VZClient instance

    Returns:
        int: Number of plugins loaded
    """
    plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins")

    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)
        print(f"📁 Created plugins directory: {plugins_dir}")
        return 0

    plugin_count = 0
    handler_count = 0

    for filename in os.listdir(plugins_dir):
        if filename.endswith(".py") and not filename.startswith("_"):
            try:
                # Import plugin module
                plugin_name = filename[:-3]
                module_name = f"plugins.{plugin_name}"

                # Remove if already loaded (for reload support)
                if module_name in sys.modules:
                    del sys.modules[module_name]

                # Import the plugin
                module = importlib.import_module(module_name)

                # Find all event handlers in the module
                plugin_handlers = 0
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)

                    # Check if it's an event handler
                    if callable(attr) and hasattr(attr, '_telethon_event'):
                        # Get the Telethon client (unwrap VZClient if needed)
                        tg_client = getattr(client, 'client', client)

                        # Add handler to client
                        tg_client.add_event_handler(attr)
                        plugin_handlers += 1
                        handler_count += 1

                plugin_count += 1
                print(f"  ✅ {plugin_name:20s} ({plugin_handlers} handlers)")

            except Exception as e:
                print(f"  ❌ {filename:20s} Error: {str(e)}")
                import traceback
                traceback.print_exc()

    print(f"\n✅ Loaded {plugin_count} plugins with {handler_count} handlers\n")
    return plugin_count

def unload_plugins(client):
    """
    Unload all plugins and remove their handlers from client.

    Args:
        client: The Telethon client or VZClient instance
    """
    # Get the Telethon client (unwrap VZClient if needed)
    tg_client = getattr(client, 'client', client)

    # Remove all handlers
    tg_client.remove_event_handler(...)  # Remove all

    # Clear global registry
    _event_handlers.clear()

    print("✅ All plugins unloaded")

print("✅ Plugin Loader Loaded")
