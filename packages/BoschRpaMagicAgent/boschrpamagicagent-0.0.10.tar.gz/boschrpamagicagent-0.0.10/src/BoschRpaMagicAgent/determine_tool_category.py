import re
from typing import Dict, List, Optional

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI


def _extract_json_object(text: str) -> Optional[str]:
    if not text:
        return None
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    return m.group(0) if m else None


def select_tool_categories(llm: ChatOpenAI, user_task: str, allowed_categories: Dict[str, str], max_categories: int = 4) -> List[str]:
    """ Select tool categories using an LLM.

    Args:
        llm(ChatOpenAI): The language model to use.
        user_task(str): The user task description.
        allowed_categories(Dict[str, str]): A dictionary of allowed category keys and their descriptions.
        max_categories(int): Maximum number of categories to select.

    Returns:
        List[str]: A list of selected category keys.

    """
    allowed_text = "\n".join([f"- {k}: {v}" for k, v in allowed_categories.items()])

    system_text = (
        "You are a strict tool-category selector.\n"
        "Return JSON only. No extra text.\n"
        f"Choose at most {max_categories} categories.\n"
        "Only choose from the allowed categories list.\n\n"
        "Allowed categories:\n"
        f"{allowed_text}\n\n"
        "Output format (JSON):\n"
        '{"categories":["CATEGORY_KEY_1","CATEGORY_KEY_2"]}'
    )

    messages = [
        SystemMessage(content=system_text),
        HumanMessage(content=f"Task:\n{user_task}")
    ]

    resp = llm.invoke(messages)
    raw_text = getattr(resp, "content", str(resp))

    json_text = _extract_json_object(raw_text) or raw_text
    data = __import__("json").loads(json_text)

    categories = data.get("categories", [])
    # clean + validate
    result = []
    for c in categories:
        c = (c or "").strip()
        if c and c not in result:
            result.append(c)

    invalid = [c for c in result if c not in allowed_categories]
    if invalid:
        raise ValueError(f"Invalid categories returned: {invalid}. Allowed: {list(allowed_categories.keys())}")

    return result[:max_categories]


