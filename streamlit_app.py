"""Streamlit front-end for the Sleep Assistant LangGraph chatbot."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import cast

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PROJECT_ROOT / "src"
for path in (PROJECT_ROOT, SRC_ROOT):
    str_path = str(path)
    if str_path not in sys.path:
        sys.path.insert(0, str_path)

from sleep_assistant.api.schemas import message_to_dict
from sleep_assistant.api.validators import validate_user_message
from sleep_assistant.config import load_environment
from sleep_assistant.graph import build_app
from sleep_assistant.graph.state import ChatState, record_user_message
from sleep_assistant.logging import configure_logging

st.set_page_config(page_title="Sleep Assistant", page_icon="😴", layout="wide")


def _empty_state() -> ChatState:
    return cast(ChatState, {"messages": [], "user_history": []})


@st.cache_resource(show_spinner=False)
def _load_graph_app():
    load_environment()
    configure_logging()
    return build_app()


try:
    graph_app = _load_graph_app()
except SystemExit as exc:
    st.error(f"Unable to start the Sleep Assistant. {exc}")
    st.stop()
except Exception as exc:  # noqa: BLE001
    st.error("The Sleep Assistant failed to initialize. Check your environment variables and try again.")
    st.exception(exc)
    st.stop()

if "chat_state" not in st.session_state:
    st.session_state.chat_state = _empty_state()

state = cast(ChatState, st.session_state.chat_state)
messages = list(state.get("messages", []))
user_turns = len(state.get("user_history", []))
current_route = state.get("current_route") or state.get("route")
retrievals = list(state.get("retrievals", []) or [])

st.title("Sleep Assistant")
st.caption("Ask about sleep hygiene, night routines, or insomnia and the assistant will route your question to the right expertise.")

with st.sidebar:
    st.header("Session")
    st.metric("User turns", user_turns)
    st.metric("Latest route", current_route or "—")
    if st.button("Start new conversation", use_container_width=True):
        st.session_state.chat_state = _empty_state()
        st.success("Conversation reset.")
        st.rerun()

    st.markdown("Configure your OpenAI and MongoDB credentials in `.env` before launching this UI.")
    st.markdown("Use `streamlit run streamlit_app.py` from the project root.")

if not messages:
    st.info("Send a message below to start a conversation.")

for payload in (message_to_dict(message) for message in messages):
    st.chat_message(payload["role"]).markdown(payload["content"])

prompt = st.chat_input("Ask about your sleep, bedtime routine, or general questions.")
if prompt:
    validation = validate_user_message(prompt)
    if not validation.is_valid:
        st.warning(validation.error_message or "Please adjust your message and try again.")
    else:
        record_user_message(state, prompt)
        with st.spinner("Thinking..."):
            try:
                updated_state = cast(ChatState, graph_app.invoke(state))
            except Exception as exc:  # noqa: BLE001
                st.error("The assistant ran into an unexpected issue. Please check the logs and try again.")
                st.exception(exc)
            else:
                st.session_state.chat_state = updated_state
        st.rerun()

st.divider()
col_left, col_right = st.columns(2)
col_left.metric("Messages", len(messages))
col_right.metric("Knowledge sources", len(retrievals))

if retrievals:
    st.subheader("Sleep knowledge snippets referenced")
    for idx, source in enumerate(retrievals, start=1):
        header_bits: list[str] = []
        source_doc = source.get("source_document")
        if source_doc:
            header_bits.append(str(source_doc))
        page_num = source.get("page_number")
        if page_num is not None:
            header_bits.append(f"Page {page_num}")
        title = header_bits[0] if header_bits else f"Snippet {idx}"
        caption = ", ".join(header_bits[1:]) if len(header_bits) > 1 else ""
        with st.expander(f"{idx}. {title}", expanded=False):
            if caption:
                st.caption(caption)
            score = source.get("score")
            if isinstance(score, (int, float)):
                st.caption(f"Relevance score: {score:.3f}")
            elif score is not None:
                st.caption(f"Relevance score: {score}")
            st.write(source.get("text") or "No text available.")
else:
    st.caption("No vector store snippets were needed for the latest reply.")
