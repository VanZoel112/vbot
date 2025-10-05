import os
import unittest

from helpers.plugin_loader import parse_plugin_file


class PluginLoaderTests(unittest.TestCase):
    def test_ping_plugin_commands_extracted(self):
        plugin_path = os.path.join(os.path.dirname(__file__), "..", "plugins", "ping.py")
        plugin_path = os.path.abspath(plugin_path)
        info = parse_plugin_file(plugin_path, "ping")
        self.assertIsNotNone(info, "parse_plugin_file should return plugin info")
        commands = info.get("commands")
        self.assertTrue(commands, "Ping plugin should have documented commands")
        self.assertTrue(any(line.startswith(".ping") for line in commands), "Ping command should be documented")


if __name__ == "__main__":
    unittest.main()
