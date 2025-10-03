"""
VZ ASSISTANT v0.0.0.69
Error Handler - Premium Emoji Error Messages with Usage Examples

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from typing import Optional


class ErrorFormatter:
    """Format error messages with premium emojis and usage examples."""

    def __init__(self, vz_emoji):
        """Initialize with VZEmojiManager instance."""
        self.vz_emoji = vz_emoji

        # Get premium error emojis
        self.error_emoji = vz_emoji.getemoji('merah')  # 👎 (premium)
        self.warning_emoji = vz_emoji.getemoji('kuning')  # ⚠️ (premium)
        self.info_emoji = vz_emoji.getemoji('gear')  # ⚙️ (premium)
        self.success_emoji = vz_emoji.getemoji('centang')  # ✅ (premium)

    def error_with_usage(
        self,
        error_message: str,
        command: str,
        usage: str,
        example: Optional[str] = None
    ) -> str:
        """
        Create error message with usage example.

        Args:
            error_message: The error description
            command: Command name (e.g., "tag")
            usage: Usage syntax (e.g., ".tag <message>")
            example: Optional example (e.g., ".tag Hello everyone!")

        Returns:
            Formatted error message with premium emojis
        """
        msg = f"{self.error_emoji} **{error_message}**\n\n"
        msg += f"{self.info_emoji} **Usage:**\n"
        msg += f"`{usage}`"

        if example:
            msg += f"\n\n{self.info_emoji} **Example:**\n`{example}`"

        return msg

    def usage_error(self, command: str, usage: str, example: Optional[str] = None) -> str:
        """Quick usage error for command."""
        return self.error_with_usage(
            f"Invalid usage for .{command}",
            command,
            usage,
            example
        )

    def failed_to_get_user(self, exception: str) -> str:
        """Error when failing to get user."""
        return f"{self.error_emoji} **Failed to get user:** `{exception}`"

    def permission_denied(self, required_permission: str) -> str:
        """Permission denied error."""
        return f"{self.error_emoji} **Permission Denied**\n\nYou need **{required_permission}** permission!"

    def warning(self, message: str) -> str:
        """Warning message with premium emoji."""
        return f"{self.warning_emoji} **{message}**"

    def info(self, message: str) -> str:
        """Info message with premium emoji."""
        return f"{self.info_emoji} **{message}**"

    def success(self, message: str) -> str:
        """Success message with premium emoji."""
        return f"{self.success_emoji} **{message}**"


def get_error_formatter(vz_emoji):
    """Get ErrorFormatter instance (convenience function)."""
    return ErrorFormatter(vz_emoji)
