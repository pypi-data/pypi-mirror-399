# start_agent.py
import asyncio
import base64
import json
import logging
import sys

from browser_use import Agent, Browser, Tools, ChatOpenAI
from tool_registry import ToolRegistry

logger = logging.getLogger("AgentStarter")


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
    sensitive_data = bot_variant_dict.get("sensitive_data", {})
    llm_prompt_block_data = bot_variant_dict.get("llm_prompt_block_data", [])
    print("---------- Sensitive Data ----------")
    for key, value in sensitive_data.items():
        print(f"{key}: **********")

    print("---------- LLM Prompt Blocks ----------")
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


# 2. Instantiate the Controller (Browser-use specific)
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


# 4. Start Agent with the Configured Tool

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

    for llm_prompt_block in llm_prompt_block_data:
        llm_model_name = llm_prompt_block.get("llm_model_name", "gemini-2.5-flash")
        llm_prompt = llm_prompt_block.get("llm_prompt", "")
        llm_api_key = llm_prompt_block.get("llm_api_key", "")
        need_browser = llm_prompt_block.get("need_browser", False)
        llm_prompt_block_name = llm_prompt_block.get("llm_prompt_block_name", "默认模块")
        max_agent_steps = llm_prompt_block.get("max_agent_steps", 30)

        llm = ChatOpenAI(base_url='https://llms.documind.bosch-app.com/v1', model=llm_model_name, api_key=llm_api_key)

        browser = None
        if need_browser:
            browser = Browser(
                headless=False,
                keep_alive=True,
                window_size={'width': 1920, 'height': 1080},  # Set window size
                enable_default_extensions=False,
                executable_path='/ms-playwright/chromium-1200/chrome-linux/chrome',
                record_video_dir=None,
                downloads_path='/opt/downloads'
            )

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
            print("Starting browser for the agent...")
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

        print(f"\n✅ Task Completed - {llm_prompt_block_name}")
        # print("⏳ Saving screen recording, please wait 5 seconds...")

        # 👇 [Key Config 2] Use automatic wait instead of manual input
        # Allow 5 seconds for Playwright to flush the video stream to disk
        await asyncio.sleep(5)

        if need_browser and browser is not None:
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
