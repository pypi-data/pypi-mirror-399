import asyncio
import functools
import time
from typing import Any, Dict, List, Optional

import httpx
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field, SecretStr

from .client import fetch_updates, send_message


def is_valid_reply(
    message: Dict[str, Any], target_chat_id: str, question_id: int
) -> bool:
    chat_match = str(message.get("chat", {}).get("id")) == str(target_chat_id)
    reply_match = message.get("reply_to_message", {}).get("message_id") == question_id
    has_text = bool(message.get("text"))
    return all([chat_match, reply_match, has_text])


def to_document(message: Dict[str, Any], question_id: int) -> Document:
    return Document(
        page_content=message["text"],
        metadata={
            "source": "telegram",
            "user_id": message.get("from", {}).get("id"),
            "username": message.get("from", {}).get("username"),
            "reply_to_msg_id": question_id,
        },
    )


def poll_for_reply(
    bot_token: str, chat_id: str, question_id: int, timeout: float, interval: float
) -> Document:
    start_time = time.monotonic()
    last_update_id = None

    with httpx.Client(timeout=None) as client:
        while (time.monotonic() - start_time) < timeout:
            updates = fetch_updates(client, bot_token, offset=last_update_id)

            for update in updates:
                last_update_id = update["update_id"] + 1
                message = update.get("message")

                if message and is_valid_reply(message, chat_id, question_id):
                    return to_document(message, question_id)

            time.sleep(interval)

    raise TimeoutError(f"No Telegram reply received within {timeout}s")


class TelegramRetriever(BaseRetriever):
    bot_token: SecretStr = Field(...)
    chat_id: str = Field(...)
    polling_timeout: float = Field(default=600.0)
    polling_interval: float = Field(default=2.0)

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None,
    ) -> List[Document]:
        token = self.bot_token.get_secret_value()

        with httpx.Client(timeout=None) as client:
            resp = send_message(client, token, self.chat_id, f"🤖 AI Question: {query}")
            question_id = resp["result"]["message_id"]

        return [
            poll_for_reply(
                token,
                self.chat_id,
                question_id,
                self.polling_timeout,
                self.polling_interval,
            )
        ]

    async def _aget_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None,
    ) -> List[Document]:
        return await asyncio.get_running_loop().run_in_executor(
            None,
            functools.partial(
                self._get_relevant_documents, query, run_manager=run_manager
            ),
        )
