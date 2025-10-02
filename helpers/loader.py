"""
VZ ASSISTANT v0.0.0.69
Plugin Loader with Event Handler Registration

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import os
import sys
import importlib
from typing import Callable, Dict, List, Optional

from telethon import events
from telethon.events.common import EventBuilder
import logging

# Create module logger
log = logging.getLogger("VZ_ASSISTANT.loader")

# Global registry for all event handlers
_event_handlers: List[Dict[str, object]] = []

# Track the plugin currently being imported (for logging/metadata)
_current_plugin: Optional[str] = None


def register_handler(
    handler: Callable,
    event_builder: Optional[EventBuilder] = None,
    plugin_name: Optional[str] = None
) -> Callable:
    """Register an event handler globally.

    Args:
        handler: The coroutine function that will handle the event.
        event_builder: The Telethon ``EventBuilder`` associated with the handler.
        plugin_name: Optional plugin name for bookkeeping.

    Returns:
        The handler itself (allows decorator usage).
    """
    _event_handlers.append({
        "handler": handler,
        "event_builder": event_builder,
        "plugin": plugin_name or getattr(handler, "__module__", "unknown"),
        "name": handler.__name__
    })
    return handler


def get_all_handlers() -> List[Dict[str, object]]:
    """Get all registered event handlers."""
    return list(_event_handlers)


def _normalise_event_builder(event_builder: Optional[object]) -> Optional[EventBuilder]:
    """Ensure we always end up with an ``EventBuilder`` instance."""
    if event_builder is None:
        return None

    if isinstance(event_builder, EventBuilder):
        return event_builder

    # Some plugins may pass the builder class instead of instance
    if isinstance(event_builder, type) and issubclass(event_builder, EventBuilder):
        return event_builder()

    return None


def load_plugins(client):
    """
    Load all plugins from plugins directory and register their handlers to client.

    Args:
        client: The Telethon client or VZClient instance

    Returns:
        int: Number of plugins loaded
    """
    global _current_plugin

    plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins")

    log.info(f"Loading plugins from: {plugins_dir}")

    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)
        log.warning(f"Created plugins directory: {plugins_dir}")
        print(f"📁 Created plugins directory: {plugins_dir}")
        return 0

    plugin_count = 0
    handler_count = 0

    # Reset registry for this load operation
    _event_handlers.clear()

    # Get the Telethon client (unwrap VZClient if needed)
    tg_client = getattr(client, 'client', client)
    log.debug(f"Using client type: {type(tg_client).__name__}")

    # Monkey patch events.register so we can capture metadata when plugins use it
    original_register = events.register

    def register_proxy(event=None, *args, **kwargs):
        decorator = original_register(event, *args, **kwargs)

        def wrapper(func):
            decorated = decorator(func)

            builder = getattr(decorated, '_telethon_event', None)
            if builder is None:
                builder = event
                normalised_builder = _normalise_event_builder(builder)
                if normalised_builder is not None:
                    setattr(decorated, '_telethon_event', normalised_builder)
                    builder = normalised_builder
            else:
                builder = _normalise_event_builder(builder)

            register_handler(decorated, builder, plugin_name=_current_plugin)
            return decorated

        return wrapper

    events.register = register_proxy

    try:
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

                    # Record how many handlers existed before importing
                    handlers_before = len(_event_handlers)

                    _current_plugin = plugin_name
                    module = importlib.import_module(module_name)
                    log.debug(f"Module imported: {module_name}")
                    _current_plugin = None

                    # Extract handlers registered during module import
                    module_handlers = _event_handlers[handlers_before:]

                    plugin_handlers = 0
                    for handler_info in module_handlers:
                        handler = handler_info["handler"]
                        builder = _normalise_event_builder(handler_info.get("event_builder"))

                        try:
                            if builder is not None:
                                tg_client.add_event_handler(handler, builder)
                            else:
                                tg_client.add_event_handler(handler)
                            plugin_handlers += 1
                            handler_count += 1
                            log.debug(
                                f"  Registered handler: {handler_info['name']} from {plugin_name}"
                            )
                        except Exception as e:
                            log.error(f"  Failed to register handler {handler_info['name']}: {e}")

                    plugin_count += 1
                    msg = f"  ✅ {plugin_name:20s} ({plugin_handlers} handlers)"
                    print(msg)
                    log.info(f"Loaded plugin: {plugin_name} with {plugin_handlers} handlers")

                except Exception as e:
                    _current_plugin = None
                    msg = f"  ❌ {filename:20s} Error: {str(e)}"
                    print(msg)
                    log.error(f"Failed to load plugin {filename}: {e}", exc_info=True)
                    import traceback
                    traceback.print_exc()
    finally:
        # Restore original register function
        events.register = original_register
        _current_plugin = None

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
