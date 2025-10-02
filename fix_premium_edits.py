#!/usr/bin/env python3
"""
Fix all event.edit() calls to use vz_client.edit_with_premium_emoji()
"""
import os
import re

PLUGINS_DIR = "plugins"

def fix_plugin_file(filepath):
    """Replace event.edit() with vz_client.edit_with_premium_emoji(event, ...)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Pattern 1: await event.edit("text")
    # Replace with: await vz_client.edit_with_premium_emoji(event, "text")
    content = re.sub(
        r'await event\.edit\((["\'])',
        r'await vz_client.edit_with_premium_emoji(event, \1',
        content
    )

    # Pattern 2: await event.edit(f"text")
    # Replace with: await vz_client.edit_with_premium_emoji(event, f"text")
    content = re.sub(
        r'await event\.edit\((f["\'])',
        r'await vz_client.edit_with_premium_emoji(event, \1',
        content
    )

    # Pattern 3: await event.edit(variable)
    # Replace with: await vz_client.edit_with_premium_emoji(event, variable)
    content = re.sub(
        r'await event\.edit\(([a-zA-Z_][a-zA-Z0-9_]*)\)',
        r'await vz_client.edit_with_premium_emoji(event, \1)',
        content
    )

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Process all plugin files"""
    fixed_count = 0

    for filename in os.listdir(PLUGINS_DIR):
        if filename.endswith('.py') and not filename.startswith('_'):
            filepath = os.path.join(PLUGINS_DIR, filename)
            if fix_plugin_file(filepath):
                print(f"✅ Fixed: {filename}")
                fixed_count += 1
            else:
                print(f"⏭️  Skipped: {filename} (no changes)")

    print(f"\n🎉 Fixed {fixed_count} plugin files!")

if __name__ == "__main__":
    main()
