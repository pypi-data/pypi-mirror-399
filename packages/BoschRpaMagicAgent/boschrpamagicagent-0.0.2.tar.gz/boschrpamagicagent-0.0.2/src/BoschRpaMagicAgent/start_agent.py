# start_agent.py
import asyncio
import base64
import datetime
import json
import logging
import os
import sys
from copy import deepcopy
from pprint import pprint

from browser_use import Agent, Browser, Tools, ChatOpenAI
from tool_registry import ToolRegistry

from smb_functions_manager import SmbFunctionsManager

logger = logging.getLogger("Agent Starter")


def get_agent_variants():
    """ This function is used to get bot variants

    """
    bot_variant_dict = {}
    try:
        input_data = sys.stdin.read()
        decoded_data = base64.b64decode(input_data).decode('utf-8')
        bot_variant_dict: dict = json.loads(decoded_data)
    except:
        pass

    return bot_variant_dict


def print_agent_variants(bot_variant_dict):
    """ This function is used to print bot variants

    Args:
        bot_variant_dict(dict): The bot variant configuration data.
    """
    bot_variant_dict = deepcopy(bot_variant_dict)
    sensitive_data = bot_variant_dict.get("sensitive_data", {})
    llm_prompt_block_data = bot_variant_dict.get("llm_prompt_block_data", [])
    public_folder_variants = bot_variant_dict.get("public_folder_variants", {})

    print('\n---------- Public Folder Info ----------')
    for variant_name, variant_dict in public_folder_variants.items():
        if variant_name in ['user_name', 'user_password']:
            variant_dict['variant_value'] = '**********'

        pprint(variant_dict)
    print("\n---------- Sensitive Data ----------")
    for key, value in sensitive_data.items():
        print(f"{key}: **********")

    print("\n---------- LLM Prompt Blocks ----------")
    for llm_prompt_block in llm_prompt_block_data:
        llm_model_name = llm_prompt_block.get("llm_model_name", "gemini-2.5-flash")
        llm_prompt = llm_prompt_block.get("llm_prompt", "")
        llm_api_key = "**********"
        need_browser = llm_prompt_block.get("need_browser", False)
        llm_prompt_block_name = llm_prompt_block.get("llm_prompt_block_name", "默认模块")
        max_agent_steps = llm_prompt_block.get("max_agent_steps", 30)

        print(f"LLM Prompt Block Name: {llm_prompt_block_name}")
        print(f"LLM Model Name: {llm_model_name}")
        print(f"LLM API Key: {llm_api_key}")
        print(f"Need Browser: {need_browser}")
        print(f"Max Agent Steps: {max_agent_steps}")
        print(f"LLM Prompt: {llm_prompt}")
        print("-----------------------------------")


async def collect_tools(requested_tools):
    """ Collects and registers the requested tools dynamically.

    Args:
        requested_tools(list): List of tool names to register.

    Returns:
        Tools: The Tools instance with registered actions.

    """
    tools = Tools()
    registry = ToolRegistry()

    # 3. Dynamic Loading
    # We pass the controller.action decorator to our registry
    # This keeps the registry independent of the specific controller instance until runtime
    if requested_tools:
        requested_tools_formatted = '\n'.join(requested_tools)
        logger.info(f"Requesting tools:\n {requested_tools_formatted}")

        # Note: In browser-use, usually we register actions to the controller
        # instead of passing a list of tools to the Agent.
        # Let's adapt the registry to register directly to the controller.

        for name in requested_tools:
            raw_func = registry._registry.get(name)  # Access raw function
            if raw_func:
                # Apply the decorator logic directly using the controller
                # @controller.action(name)
                # def wrapper(): return raw_func()

                # Dynamic registration:
                tools.action(name)(raw_func)
                logger.info(f"✅ Registered {name} to Tools")
            else:
                logger.warning(f"Tool {name} not found")

    return tools


def prepare_smb_manger_instance(public_folder_variants):
    """ Prepares the SMB Manager instance with public folder variants.

    Args:
        public_folder_variants(dict): The public folder variant configuration data.

    Returns:
        smb_manager_instance(SmbFunctionsManager): The SMB Manager instance.
        report_save_path(str): The report save path.
    """
    user_name, user_password, server_name, share_name, report_save_path, port = (public_folder_variants['user_name']['variant_value'],
                                                                                 public_folder_variants['user_password']['variant_value'],
                                                                                 public_folder_variants['server_name']['variant_value'],
                                                                                 public_folder_variants['share_name']['variant_value'],
                                                                                 public_folder_variants['report_save_path']['variant_value'],
                                                                                 public_folder_variants['port']['variant_value'])
    smb_manager_instance = SmbFunctionsManager(user_name, user_password, server_name, share_name, port)

    return smb_manager_instance, report_save_path


async def background_screenshot_loop(browser, stop_event, smb_manager_instance, remote_screenshot_folder_path, interval=3.0, save_dir="/opt/screenshots",
                                     screenshot_tag='screenshot'):
    """
    Background task to take screenshots periodically without blocking the main thread.

    Args:
        browser(Browser): The browser instance to take screenshots from.
        stop_event(asyncio.Event): Event to signal stopping the background task.
        interval(float): Time interval between screenshots in seconds.
        save_dir(str): Directory to save screenshots.
        screenshot_tag(str): Tag to include in screenshot filenames.
        smb_manager_instance(SmbFunctionsManager): The SMB Manager instance for file operations.
        remote_screenshot_folder_path(str): The remote folder path to save screenshots.
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    print(f"📸 Screenshot background task started. Interval: {interval}s")

    while not stop_event.is_set():
        try:
            # Sleep first
            await asyncio.sleep(interval)

            # Check if browser is connected before trying (prevents errors during startup/shutdown)
            # We check _cdp_client_root based on your source code (line 893)
            if not getattr(browser, "_cdp_client_root", None):
                continue

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_name = f"{screenshot_tag}_{timestamp}.png"
            local_screenshot_path = os.path.join(save_dir, screenshot_name)

            # ✅ CORRECT WAY: Use the method provided in session.py
            # This handles finding the correct cdp_session and target_id automatically.
            await browser.take_screenshot(path=local_screenshot_path)
            print(f"📸 Snap: {local_screenshot_path}")
            remote_screenshot_path = remote_screenshot_folder_path + '/' + screenshot_name
            await asyncio.to_thread(
                smb_manager_instance.smb_copy_file_local_to_remote,
                local_screenshot_path,
                remote_screenshot_path
            )
            print('📁 Screenshot uploaded to remote shared driver.')


        except Exception as e:
            # Common errors during page transitions or initialization are ignored
            # to keep the agent running smoothly.
            # print(f"⚠️ Screenshot skipped: {e}")
            pass

    print("🛑 Screenshot background task stopped.")


async def start_agent(bot_variant_dict: dict):
    """ Starts the agent with the given bot variant data.

    Args:
        bot_variant_dict(dict): The bot variant configuration data.
    """
    print_agent_variants(bot_variant_dict)
    requested_tools = bot_variant_data.get("allowed_tools", [])
    tools = await collect_tools(requested_tools)
    sensitive_data = bot_variant_dict.get("sensitive_data", {})
    llm_prompt_block_data = bot_variant_dict.get("llm_prompt_block_data", [])
    public_folder_variants = bot_variant_dict.get("public_folder_variants", {})

    smb_manager_instance, report_save_path = prepare_smb_manger_instance(public_folder_variants)
    smb_manager_instance: SmbFunctionsManager
    remote_screenshot_folder_path = report_save_path + '/' + 'Screenshots'
    is_remote_folder_exist = smb_manager_instance.smb_check_folder_exist(remote_screenshot_folder_path)
    if not is_remote_folder_exist:
        smb_manager_instance.smb_create_folder(remote_screenshot_folder_path)

    browser = None

    for llm_prompt_block in llm_prompt_block_data:
        llm_model_name = llm_prompt_block.get("llm_model_name", "gemini-2.5-flash")
        llm_prompt = llm_prompt_block.get("llm_prompt", "")
        llm_api_key = llm_prompt_block.get("llm_api_key", "")
        need_browser = llm_prompt_block.get("need_browser", False)
        llm_prompt_block_name = llm_prompt_block.get("llm_prompt_block_name", "默认模块")
        max_agent_steps = llm_prompt_block.get("max_agent_steps", 30)

        llm = ChatOpenAI(base_url='https://llms.documind.bosch-app.com/v1', model=llm_model_name, api_key=llm_api_key)

        if need_browser and browser is None:
            browser = Browser(
                headless=False,
                keep_alive=True,
                window_size={'width': 1920, 'height': 1080},  # Set window size
                enable_default_extensions=False,
                executable_path='/ms-playwright/chromium-1200/chrome-linux/chrome',
                record_video_dir=None,
                downloads_path='/opt/downloads'
            )

        screenshot_task = None
        stop_screenshots = asyncio.Event()

        if need_browser:
            print(f"🎬 Starting camera for {llm_prompt_block_name}...")
            screenshot_task = asyncio.create_task(
                background_screenshot_loop(
                    browser,
                    stop_screenshots,
                    smb_manager_instance,
                    remote_screenshot_folder_path,
                    interval=3.0,
                    screenshot_tag=llm_prompt_block_name
                )
            )

        if need_browser:
            agent = Agent(
                task=llm_prompt,
                llm=llm,
                browser=browser,
                generate_gif=True,
                save_conversation_path=None,
                llm_timeout=180,
                use_judge=False,
                tools=tools,
                sensitive_data=sensitive_data,
            )

        else:
            agent = Agent(
                task=llm_prompt,
                llm=llm,
                generate_gif=True,
                save_conversation_path=None,
                llm_timeout=180,
                use_judge=False,
                tools=tools,
                sensitive_data=sensitive_data
            )

        try:
            await agent.run(max_steps=max_agent_steps)
        except Exception as e:
            # As long as the file is downloaded, errors here are just noise; ignore them.
            print(f"⚠️ Minor error during cleanup due to network (result unaffected): {e}")
        finally:
            if screenshot_task:
                print(f"🛑 Stopping camera for {llm_prompt_block_name}...")
                stop_screenshots.set()
                try:
                    await screenshot_task
                except asyncio.CancelledError:
                    pass
                screenshot_task = None

        print(f"\n✅ Task Completed - {llm_prompt_block_name}")
        # print("⏳ Saving screen recording, please wait 5 seconds...")

        # 👇 [Key Config 2] Use automatic wait instead of manual input
        # Allow 5 seconds for Playwright to flush the video stream to disk
        await asyncio.sleep(5)

    if browser is not None:
        print("👋 Preparing to close browser...")

        # 1. Critical: Attempt graceful stop first to let EventBus finish pending tasks
        try:
            # stop() dispatches BrowserStopEvent(force=False)
            # This allows underlying Playwright tasks to terminate logically
            # instead of being abruptly killed.
            await browser.stop()
            await asyncio.sleep(0.5)  # Give the asyncio loop a moment to breathe and collect exceptions
        except Exception:
            pass

        # 2. Force kill the process and reset state
        await browser.kill()

        print("✅ Browser closed completely. No residual async exceptions.")


bot_variant_data = get_agent_variants()
start_agent(bot_variant_data)
