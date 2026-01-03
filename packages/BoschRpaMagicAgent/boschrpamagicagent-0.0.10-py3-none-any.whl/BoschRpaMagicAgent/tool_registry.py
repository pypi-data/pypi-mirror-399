# tool_registry.py
import logging
from browser_use import Tools, ChatOpenAI

from determine_tool_category import select_tool_categories
# Import your raw functions
from tools.share_driver_functions import *
from tools.send_email_functions import *
from tools.download_page_clean import *

logger = logging.getLogger("ToolRegistry")

ALLOWED_CATEGORY_LIST = {
    "SMB_READONLY": "SMB read-only: stat/list/download (remote->local).",
    "SMB_WRITE_COPY_ONLY": "SMB copy/upload: local->remote or remote->remote copy.",
    "SMB_WRITE_MKDIR": "Create remote folders.",
    "SAP_WEBGUI_DOWNLOAD": "SAP WebGUI download page helpers.",
    "EMAIL_SMTP_SEND": "Send email via SMTP.",
}


class ToolRegistry:
    def __init__(self):
        # 1. Define the Mapping: "String Name" -> Raw Function
        # This is your "Menu" of available capabilities.
        self._registry = {
            # SMB - default safe
            "SMB_READONLY": [
                smb_get_remote_file_metadata,
                smb_get_remote_folder_metadata,
                smb_list_remote_folder_entries,
                smb_download_remote_file_to_local,
            ],

            # SMB - write operations (copy/upload)
            "SMB_WRITE_COPY_ONLY": [
                smb_copy_remote_file_to_remote,
                smb_upload_local_file_to_remote,
                smb_upload_bytesio_to_remote_file,  # 可选：最好不给 Agent
            ],

            # SMB - mkdir (optional)
            "SMB_WRITE_MKDIR": [
                smb_create_remote_folder,
            ],

            # SAP
            "SAP_WEBGUI_DOWNLOAD": [
                clean_sap_download_page,
            ],

            # Email
            "EMAIL_SMTP_SEND": [
                send_email_via_smtp_server,
            ],
        }


    @staticmethod
    def collect_tools(api_key, llm_prompt):
        """ Collects and registers the requested tools dynamically.

        Args:

        Returns:
            Tools: The Tools instance with registered actions.

        """
        tools = Tools()
        registry = ToolRegistry()

        llm = ChatOpenAI(
            model='gpt5-mini',
            temperature=0,
            timeout=60,
            max_retries=2,
            base_url='https://llms.documind.bosch-app.com/v1',
            api_key=api_key,
        )

        tool_category_list = select_tool_categories(llm, user_task=llm_prompt, allowed_categories=ALLOWED_CATEGORY_LIST, max_categories=4)

        # 3. Dynamic Loading
        # We pass the controller.action decorator to our registry
        # This keeps the registry independent of the specific controller instance until runtime
        if tool_category_list:
            requested_tools_formatted = '\n'.join(tool_category_list)
            logger.info(f"Requesting tools:\n {requested_tools_formatted}")

            for tool_category in tool_category_list:
                raw_func_list = registry._registry.get(tool_category)  # Access raw function
                if raw_func_list:
                    # Dynamic registration:
                    for raw_func in raw_func_list:
                        tools.action(tool_category)(raw_func)
                        logger.info(f"✅ Registered {tool_category} to Tools")
                else:
                    logger.warning(f"Tool {tool_category} not found")

        return tools
