"""Chat endpoints for the Sleep Assistant API."""

from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import APIRouter, Depends
from langchain_core.messages import AIMessage

from sleep_assistant.api.deps import Sessions, get_graph_app, get_sessions_store
from sleep_assistant.api.schemas import ChatRequest, ChatResponse, message_to_dict
from sleep_assistant.api.validators import validate_user_message
from sleep_assistant.graph.state import record_user_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    graph_app=Depends(get_graph_app),
    sessions: Sessions = Depends(get_sessions_store),
) -> ChatResponse:
    """Process a chat turn routed through the LangGraph application."""

    session_id = request.session_id or str(uuid4())
    validation = validate_user_message(request.message)
    if not validation.is_valid:
        logger.info("Rejected message for session %s: %s", session_id, validation.error_message)
        existing_state = sessions.get(session_id)
        messages_payload = (
            [message_to_dict(msg) for msg in existing_state.get("messages", [])] if existing_state else []
        )
        return ChatResponse(
            session_id=session_id,
            reply=validation.error_message or "Please adjust your message and try again.",
            route="validation",
            messages=messages_payload,
        )

    message = request.message.strip()
    state = sessions.setdefault(session_id, {"messages": [], "user_history": []})
    record_user_message(state, message)
    updated_state = graph_app.invoke(state)
    sessions[session_id] = updated_state

    # Extract reply from AI message, converting content to string if needed
    reply = "I'm not sure how to respond to that."
    for msg in reversed(updated_state.get("messages", [])):
        if isinstance(msg, AIMessage):
            content = msg.content
            reply = content if isinstance(content, str) else str(content)
            break
    route = updated_state.get("current_route") or updated_state.get("route", "sleep")
    logger.info("Session %s used route '%s'.", session_id, route)

    messages_payload = [message_to_dict(msg) for msg in updated_state.get("messages", [])]
    sources_payload = []
    for item in updated_state.get("retrievals", []) or []:
        if isinstance(item, dict):
            sources_payload.append(
                {
                    "text": item.get("text"),
                    "page_number": item.get("page_number"),
                    "source_document": item.get("source_document"),
                    "score": item.get("score"),
                }
            )
    return ChatResponse(
        session_id=session_id,
        reply=reply,
        route=route,
        messages=messages_payload,
        sources=sources_payload,
    )
