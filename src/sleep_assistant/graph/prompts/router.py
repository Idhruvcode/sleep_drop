"""Prompt template used for routing user queries."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate


def get_router_prompt() -> ChatPromptTemplate:
    """Return the classification prompt used to select the conversation route."""

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are the intent classifier for the Sleep Assistant.\n\n"
                "Your task is to determine whether the user's message is:\n"
                '- "general" -> only if it is a greeting or simple polite small talk (e.g. '
                '"hi", "hello", "good morning", "hey", "how are you", "good evening").\n'
                '- "sleep" -> for any other type of message, especially if it asks for information, '
                "advice, help, or mentions health, rest, tiredness, routines, lifestyle, "
                "wellness, nutrition, supplements, stress, recovery, relaxation, bedtime habits, "
                "or anything that could affect sleep directly or indirectly.\n\n"
                "If it is a general greeting, the chatbot will only respond politely to the greeting.\n"
                "If it is anything else, it will be treated as a sleep-related query.\n\n"
                "Respond with exactly one lowercase word:\n"
                '- "sleep"\n'
                '- "general"\n\n'
                "No extra words or explanations.\n\n"
                "Examples:\n\n"
                'Sleep -> (respond "sleep")\n'
                '- {{"message": "Nutrition, supplements and recipes"}}\n'
                '- {{"message": "Why do I feel tired in the morning?"}}\n'
                '- {{"message": "What can help me relax at night?"}}\n'
                '- {{"message": "How do I stop waking up in the middle of the night?"}}\n'
                '- {{"message": "I feel exhausted all day. What should I do?"}}\n'
                '- {{"message": "Foods that help with rest or recovery"}}\n\n'
                'General -> (respond "general")\n'
                '- {{"message": "Hi"}}\n'
                '- {{"message": "Hello, how are you?"}}\n'
                '- {{"message": "Good morning"}}\n'
                '- {{"message": "Hey"}}\n'
                '- {{"message": "Good evening"}}',
            ),
            ("human", "{question}"),
        ]
    )


__all__ = ["get_router_prompt"]
