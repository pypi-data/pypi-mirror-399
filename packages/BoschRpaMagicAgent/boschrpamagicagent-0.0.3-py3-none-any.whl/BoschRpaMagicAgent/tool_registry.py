# tool_registry.py
import logging

# Import your raw functions
from tools import share_driver_functions

logger = logging.getLogger("ToolRegistry")


class ToolRegistry:
    def __init__(self):
        # 1. Define the Mapping: "String Name" -> Raw Function
        # This is your "Menu" of available capabilities.
        self._registry = {
            "smb_copy_file_local_to_remote": share_driver_functions.smb_copy_file_local_to_remote,
        }

    def get_tools(self, tool_names: list[str], tool_decorator):
        """
        Dynamically applies the decorator to the requested functions.

        Args:
            tool_names: List of strings e.g. ["google_search", "teams_notify"]
            tool_decorator: The actual @tool.action function/object

        Returns:
            List of decorated tools ready for the Agent.
        """
        active_tools = []

        # Deduplicate names
        unique_names = set(tool_names)

        for name in unique_names:
            raw_func = self._registry.get(name)

            if not raw_func:
                logger.warning(f"⚠️ Tool '{name}' requested but not found in registry. Skipping.")
                continue

            # --- The Magic Happens Here ---
            # We manually apply the decorator: @tool.action
            # equivalent to: decorated_func = tool.action(raw_func)
            try:
                logger.info(f"🔧 Loading Tool: {name}")
                decorated_tool = tool_decorator(raw_func)
                active_tools.append(decorated_tool)
            except Exception as e:
                logger.error(f"❌ Failed to decorate tool '{name}': {e}")

        return active_tools
