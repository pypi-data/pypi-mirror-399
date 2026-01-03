from typing import Any, Dict, List, Optional

import httpx


def telegram_url(
    bot_token: str, method: str, base_url: str = "https://api.telegram.org"
) -> str:
    """Builds a URL for the Telegram Bot API."""
    return f"{base_url}/bot{bot_token}/{method}"


def send_message(
    client: httpx.Client, bot_token: str, chat_id: str, text: str
) -> Dict[str, Any]:
    """Dispatches a text message to a specific chat."""
    response = client.post(
        telegram_url(bot_token, "sendMessage"), json={"chat_id": chat_id, "text": text}
    )
    response.raise_for_status()
    return response.json()


def fetch_updates(
    client: httpx.Client,
    bot_token: str,
    offset: Optional[int] = None,
    timeout: int = 10,
) -> List[Dict[str, Any]]:
    """Retrieves a list of updates from the Telegram server."""
    params = {
        "timeout": timeout,
        "allowed_updates": ["message"],
        **({"offset": offset} if offset is not None else {}),
    }

    response = client.get(
        telegram_url(bot_token, "getUpdates"), params=params, timeout=timeout + 5
    )
    response.raise_for_status()
    return response.json().get("result", [])
