"""Sleep-specialist node for the LangGraph chatbot."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage
from langchain_openai import OpenAIEmbeddings

from sleep_assistant.graph.state import (
    MAX_USER_HISTORY,
    ChatState,
    RetrievedDocument,
    get_conversation_window,
    get_last_user_message,
    get_recent_user_messages,
)
from sleep_assistant.graph.prompts.sleep import get_sleep_prompt

logger = logging.getLogger(__name__)


def build_sleep_chain(sleep_llm):
    """Return an LLM chain for answering sleep-related questions."""

    sleep_prompt = get_sleep_prompt()
    return sleep_prompt | sleep_llm


def _extract_text(metadata: Dict[str, object]) -> Optional[str]:
    """Return the best-guess text field from vector metadata."""

    text_keys = (
        "text",
        "content",
        "chunk",
        "chunk_text",
        "page_content",
        "text_preview",
    )
    for key in text_keys:
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def make_sleep_node(vector_store: Any, embedder: OpenAIEmbeddings, sleep_chain):
    """Build the LangGraph node for sleep-related responses."""

    def node(state: ChatState) -> Dict[str, object]:
        latest_user = get_last_user_message(state) or ""
        if not latest_user:
            return {"messages": [AIMessage(content="I didn't catch that. Could you repeat your question?")]}

        recent_user_history = get_recent_user_messages(state, limit=MAX_USER_HISTORY)
        if recent_user_history:
            query_text = " ".join(recent_user_history[-2:])
        else:
            query_text = latest_user

        history_lines = get_conversation_window(state, limit=MAX_USER_HISTORY * 2)
        history_text = "\n".join(history_lines) if history_lines else "No prior conversation."

        query_embedding = embedder.embed_query(query_text)
        results = vector_store.query(vector=query_embedding, top_k=5, include_metadata=True)

        contexts: List[str] = []
        retrievals: List[RetrievedDocument] = []
        matches = getattr(results, "matches", None) or []
        for match in matches:
            metadata = getattr(match, "metadata", None) or {}
            text = _extract_text(metadata)
            if text:
                page_number = metadata.get("page_number") or metadata.get("page")
                source_document = metadata.get("source_document") or metadata.get("source")
                label_parts = []
                if source_document:
                    label_parts.append(f"Source: {source_document}")
                if page_number is not None:
                    label_parts.append(f"Page: {page_number}")
                label = f"[{', '.join(label_parts)}]\n" if label_parts else ""
                contexts.append(f"{label}{text}".strip())

                retrieved: RetrievedDocument = {"text": text}
                if page_number is not None:
                    retrieved["page_number"] = page_number
                if source_document:
                    retrieved["source_document"] = source_document
                score = getattr(match, "score", None)
                if score is not None:
                    retrieved["score"] = score
                retrievals.append(retrieved)

        if contexts:
            combined_context = "\n\n".join(contexts)
            logger.info("Sleep node retrieved %d document snippets from MongoDB vector search.", len(contexts))
            ai_message = sleep_chain.invoke(
                {"context": combined_context, "question": latest_user, "history": history_text}
            )
        else:
            logger.info("Sleep node found no relevant MongoDB matches for the query.")
            ai_message = AIMessage(
                content="I'm not sure. I couldn't find relevant information about that in my sleep knowledge base."
            )
        return {
            "messages": [ai_message],
            "route": "sleep",
            "current_route": "sleep",
            "last_node": "sleep",
            "retrievals": retrievals,
        }

    return node
