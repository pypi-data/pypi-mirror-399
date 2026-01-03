"""
TelegramRetriever Demo: Human-in-the-Loop Orchestrator
=====================================================

DESCRIPTION:
This script demonstrates how to use DSPy with the TelegramRetriever to create a
"Human-in-the-loop" system. When the AI (using Ollama) cannot answer a query,
it will reach out to a human expert via a Telegram bot for clarification.

PREREQUISITES:
1. Install dependencies:
   pip install -U dspy telegram-retriever

2. Ensure Ollama is running locally with the specified model:
   ollama run qwen3-vl:4b-instruct-q4_K_M

3. Have your Telegram Bot Token and Chat ID ready.

RUNNING THE DEMO:
python examples/human_in_the_loop_demo.py
"""

import dspy
from telegram_retriever import TelegramRetriever


class TelegramExpertConsultation(dspy.Signature):
    """
    Resolve complex queries by synthesizing provided expert context.
    If the context is insufficient, specify what is missing.
    """

    question = dspy.InputField()
    expert_context = dspy.InputField(
        desc="Direct feedback from a human expert via Telegram."
    )
    answer = dspy.OutputField(desc="A comprehensive response based on expert input.")


def create_ollama_language_model(model_identifier):
    return dspy.LM(model_identifier, api_base="http://localhost:11434", cache=False)


def initialize_telegram_bridge(bot_token, chat_id):
    return TelegramRetriever(bot_token=bot_token, chat_id=chat_id)


def query_human_expert_via_telegram(retriever, query):
    expert_responses = retriever.invoke(query)

    if not expert_responses:
        return "The human expert is currently unreachable or provided no input."

    return expert_responses[0].page_content


class HumanInTheLoopOrchestrator(dspy.Module):
    def __init__(self, bot_token, chat_id):
        super().__init__()

        self.bridge = initialize_telegram_bridge(bot_token, chat_id)

        self.reasoner = dspy.ReAct(
            TelegramExpertConsultation,
            tools=[
                dspy.Tool(
                    lambda query: query_human_expert_via_telegram(self.bridge, query),
                    name="consult_human_expert",
                    desc="Useful when local knowledge is insufficient and you need real-time human clarification.",
                )
            ],
        )

    def forward(self, user_query):
        prediction = self.reasoner(
            question=user_query, expert_context="Awaiting human input..."
        )
        return prediction.answer


def display_session_header():
    print("\n" + "=" * 50)
    print("AI-HUMAN HYBRID TERMINAL")
    print("Type 'exit' or 'quit' to terminate the session.")
    print("=" * 50 + "\n")


def execute_interactive_consultation_loop(assistant):
    display_session_header()

    while True:
        try:
            user_input = input("User > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nTerminating session. Goodbye.")
            break

        if user_input.lower() in ["exit", "quit", "q"]:
            print("Terminating session. Goodbye.")
            break

        if not user_input:
            continue

        try:
            assistant_response = assistant(user_input)
            print(f"\nAssistant > {assistant_response}\n")
        except Exception as error:
            print(f"\nSystem Error > {str(error)}\n")


def main():
    # --- CONFIGURATION ---
    # Replace the placeholders below with your actual credentials
    TELEGRAM_CONFIG = {
        "bot_token": "YOUR_BOT_TOKEN_HERE",  # e.g., "123456:ABC-DEF..."
        "chat_id": "YOUR_CHAT_ID_HERE",  # e.g., "987654321"
    }

    OLLAMA_CONFIG = {"model_identifier": "ollama_chat/qwen3-vl:4b-instruct-q4_K_M"}
    # ---------------------

    dspy.configure(lm=create_ollama_language_model(OLLAMA_CONFIG["model_identifier"]))

    hybrid_assistant = HumanInTheLoopOrchestrator(
        bot_token=TELEGRAM_CONFIG["bot_token"],
        chat_id=TELEGRAM_CONFIG["chat_id"],
    )

    execute_interactive_consultation_loop(hybrid_assistant)


if __name__ == "__main__":
    main()
