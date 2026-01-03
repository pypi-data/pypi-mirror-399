# telegram-retriever

**telegram-retriever** is a functional, human-in-the-loop extension for LangChain. It allows an LLM agent to pause execution, send a query to a specific Telegram user, and synchronously wait for a text-based reply.

## 🧠 The Functional Pipeline

The retriever follows a strict data-flow architecture:

* **Dispatch**: Sends the AI's question to the target chat via the Telegram Bot API.
* **Poll**: Enters a stateless polling loop to fetch updates.
* **Filter**: Validates incoming data to ensure it is a text-based "Reply-To" message from the correct user.
* **Transform**: Converts the validated Telegram message into a LangChain `Document`.

## 🚀 Installation

```bash
pip install telegram-retriever

```

## 🛠 Usage

### Synchronous (Blocking)

Perfect for scripts where the process should wait for human intervention.

```python
import os
from telegram_retriever import TelegramRetriever

retriever = TelegramRetriever(
    bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
    chat_id=os.getenv("TELEGRAM_CHAT_ID")
)

# Execution pauses here until the human replies on Telegram
docs = retriever.invoke("Do you approve the budget for Q3?")
print(f"Human response: {docs[0].page_content}")

```

### Asynchronous (Non-blocking)

Recommended for FastAPI or LangServe applications to keep the event loop free.

```python
docs = await retriever.ainvoke("Should I trigger the deployment?")

```

## ⚙️ Configuration

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `bot_token` | `SecretStr` | **Required** | Your Telegram Bot API Token. |
| `chat_id` | `str` | **Required** | The target User ID or Group ID. |
| `polling_timeout` | `float` | `600.0` | Seconds to wait before timing out. |
| `polling_interval` | `float` | `2.0` | Seconds between update checks. |

## 🧪 Development

The project is built on pure functions, making testing simple and reliable.

```bash
# Install test dependencies
pip install .[test]

# Run the functional test suite
pytest

```

## 🎮 Demo: Human-in-the-Loop Workflow

This demo uses the script located at [`examples/chatbot.py`](./examples/chatbot.py) to showcase how the AI agent (via DSPy) intelligently decides when human intervention is necessary.

### How it Works:
1. **Direct AI Response (Autonomous):** When the user asks a straightforward math question (*"What's 127 x 23?"*), the AI handles it locally using its internal knowledge. It does **not** trigger a Telegram notification because the task is simple and clear.
2. **Human-in-the-Loop (Triggered):** When the user asks a subjective or context-heavy question (*"What's so special about 67?"*), the AI recognizes its own limitations.
3. **Telegram Integration:** The AI pauses, sends the query to the human expert via Telegram, and waits for a reply. 
4. **Synthesis:** Once the human replies (*"It's an internet meme"*), the AI synthesizes this "expert context" into a comprehensive final answer for the user.

![Human-in-the-Loop Demo Screenshot](./examples/chatbot-demo.jpg)
*(Note: Sensitive Telegram identifiers have been safely redacted in this image.)*