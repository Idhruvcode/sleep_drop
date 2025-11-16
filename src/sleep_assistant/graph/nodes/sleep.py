"""Sleep-specialist node for the LangGraph chatbot."""

from __future__ import annotations

import logging
from typing import Dict, List

from langchain_core.messages import AIMessage
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone

from sleep_assistant.graph.state import ChatState, get_last_user_message
from sleep_assistant.graph.prompts.sleep import get_sleep_prompt

logger = logging.getLogger(__name__)


def build_sleep_chain(sleep_llm):
    """Return an LLM chain for answering sleep-related questions."""

    sleep_prompt = get_sleep_prompt()
    return sleep_prompt | sleep_llm


def make_sleep_node(index: Pinecone.Index, embedder: OpenAIEmbeddings, sleep_chain):
    """Build the LangGraph node for sleep-related responses."""

    def node(state: ChatState) -> Dict[str, object]:
        latest_user = get_last_user_message(state) or ""
        if not latest_user:
            return {"messages": [AIMessage(content="I didn't catch that. Could you repeat your question?")]}

        query_embedding = embedder.embed_query(latest_user)
        results = index.query(vector=query_embedding, top_k=5, include_metadata=True)

        contexts: List[str] = []
        matches = getattr(results, "matches", None) or []
        for match in matches:
            metadata = getattr(match, "metadata", None) or {}
            text = metadata.get("text")
            if text:
                contexts.append(text)

        if contexts:
            combined_context = "\n\n".join(contexts)
            logger.info("Sleep node retrieved %d document snippets from Pinecone.", len(contexts))
            ai_message = sleep_chain.invoke({"context": combined_context, "question": latest_user})
        else:
            logger.info("Sleep node found no relevant Pinecone matches for the query.")
            ai_message = AIMessage(
                content="I'm not sure. I couldn't find relevant information about that in my sleep knowledge base."
            )
        return {"messages": [ai_message], "route": "sleep", "current_route": "sleep", "last_node": "sleep"}

    return node
