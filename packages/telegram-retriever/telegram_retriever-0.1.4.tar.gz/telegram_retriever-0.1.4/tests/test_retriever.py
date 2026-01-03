from unittest.mock import patch

import pytest
from langchain_core.documents import Document

from telegram_retriever.retriever import TelegramRetriever, is_valid_reply, to_document

TOKEN = "123:ABC"
CHAT_ID = "999"
Q_ID = 100


def test_reply_validation_logic():
    valid_msg = {
        "chat": {"id": 999},
        "reply_to_message": {"message_id": 100},
        "text": "Yes",
    }
    wrong_chat = {
        "chat": {"id": 111},
        "reply_to_message": {"message_id": 100},
        "text": "Yes",
    }
    no_text = {
        "chat": {"id": 999},
        "reply_to_message": {"message_id": 100},
        "sticker": {},
    }

    assert is_valid_reply(valid_msg, CHAT_ID, Q_ID) is True
    assert is_valid_reply(wrong_chat, CHAT_ID, Q_ID) is False
    assert is_valid_reply(no_text, CHAT_ID, Q_ID) is False


def test_document_transformation():
    msg = {"text": "The Answer", "from": {"id": 42, "username": "deepthought"}}
    doc = to_document(msg, Q_ID)

    assert isinstance(doc, Document)
    assert doc.page_content == "The Answer"
    assert doc.metadata["user_id"] == 42
    assert doc.metadata["reply_to_msg_id"] == Q_ID


@pytest.fixture
def mock_network():
    with patch("httpx.Client") as mock_cls:
        client = mock_cls.return_value.__enter__.return_value
        yield client


def test_successful_retrieval_flow(mock_network):
    retriever = TelegramRetriever(
        bot_token=TOKEN, chat_id=CHAT_ID, polling_interval=0.0
    )

    mock_network.post.return_value.json.return_value = {
        "ok": True,
        "result": {"message_id": Q_ID},
    }

    mock_network.get.return_value.json.return_value = {
        "ok": True,
        "result": [
            {
                "update_id": 1,
                "message": {
                    "chat": {"id": int(CHAT_ID)},
                    "reply_to_message": {"message_id": Q_ID},
                    "text": "Confirmed",
                    "from": {"id": 1, "username": "user"},
                },
            }
        ],
    }

    docs = retriever.invoke("Ready?")

    assert len(docs) == 1
    assert docs[0].page_content == "Confirmed"


@pytest.mark.asyncio
async def test_async_delegation(mock_network):
    retriever = TelegramRetriever(bot_token=TOKEN, chat_id=CHAT_ID)

    mock_network.post.return_value.json.return_value = {"result": {"message_id": Q_ID}}
    mock_network.get.return_value.json.return_value = {
        "result": [
            {
                "update_id": 1,
                "message": {
                    "chat": {"id": int(CHAT_ID)},
                    "reply_to_message": {"message_id": Q_ID},
                    "text": "Async",
                },
            }
        ]
    }

    docs = await retriever.ainvoke("Go?")
    assert docs[0].page_content == "Async"


def test_polling_timeout_exhaustion(mock_network):
    retriever = TelegramRetriever(
        bot_token=TOKEN, chat_id=CHAT_ID, polling_timeout=0.1, polling_interval=0.01
    )

    mock_network.post.return_value.json.return_value = {"result": {"message_id": Q_ID}}
    mock_network.get.return_value.json.return_value = {"result": []}

    with pytest.raises(TimeoutError):
        retriever.invoke("Wait forever?")
