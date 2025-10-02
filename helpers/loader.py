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
import logging

# Create module logger
log = logging.getLogger("VZ_ASSISTANT.loader")

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

    log.info(f"Loading plugins from: {plugins_dir}")

    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)
        log.warning(f"Created plugins directory: {plugins_dir}")
        print(f"📁 Created plugins directory: {plugins_dir}")
        return 0

    plugin_count = 0
    handler_count = 0

    # Get the Telethon client (unwrap VZClient if needed)
    tg_client = getattr(client, 'client', client)
    log.debug(f"Using client type: {type(tg_client).__name__}")

    for filename in sorted(os.listdir(plugins_dir)):
        if filename.endswith(".py") and not filename.startswith("_"):
            try:
                # Import plugin module
                plugin_name = filename[:-3]
                module_name = f"plugins.{plugin_name}"

                log.debug(f"Loading plugin: {plugin_name}")

                # Remove if already loaded (for reload support)
                if module_name in sys.modules:
                    log.debug(f"Reloading module: {module_name}")
                    del sys.modules[module_name]

                # Import the plugin
                module = importlib.import_module(module_name)
                log.debug(f"Module imported: {module_name}")

                # Find all event handlers in the module
                plugin_handlers = 0
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)

                    # Check if it's an event handler
                    if callable(attr) and hasattr(attr, '_telethon_event'):
                        try:
                            # Add handler to client
                            tg_client.add_event_handler(attr)
                            plugin_handlers += 1
                            handler_count += 1
                            log.debug(f"  Registered handler: {attr_name} from {plugin_name}")
                        except Exception as e:
                            log.error(f"  Failed to register handler {attr_name}: {e}")

                plugin_count += 1
                msg = f"  ✅ {plugin_name:20s} ({plugin_handlers} handlers)"
                print(msg)
                log.info(f"Loaded plugin: {plugin_name} with {plugin_handlers} handlers")

            except Exception as e:
                msg = f"  ❌ {filename:20s} Error: {str(e)}"
                print(msg)
                log.error(f"Failed to load plugin {filename}: {e}", exc_info=True)
                import traceback
                traceback.print_exc()

    summary = f"Loaded {plugin_count} plugins with {handler_count} handlers"
    print(f"\n✅ {summary}\n")
    log.info(summary)

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
