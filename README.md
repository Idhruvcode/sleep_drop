# Sleep Assistant Service

The Sleep Assistant is a LangGraph-powered multi-agent experience that routes every user message to the right expertise. It distinguishes casual greetings from sleep-focused questions, enriches sleep conversations with Pinecone-backed context retrieval, and serves responses through a CLI helper and a FastAPI endpoint.

---

## Features

- FastAPI service for real-time chat over HTTP on port 8001.
- CLI companion (`scripts/run_chatbot.py`) for local conversational testing.
- LangGraph orchestration with an intent router, general chat node, and sleep-specialist node.
- Sleep knowledge base powered by Pinecone vector search and OpenAI embeddings.
- Environment-driven configuration with a simple `.env` workflow.
- Optional observability through LangSmith and structured logging.

## Conversation Flow

1. The router prompt classifies each incoming message as either `general` or `sleep`.
2. Greetings and small talk are answered by the general node via an LLM tuned for casual conversation.
3. Sleep-related questions trigger Pinecone retrieval, combining matched snippets with a dedicated sleep prompt before responding.

---

## Prerequisites

- Python 3.11 (CPython recommended)
- OpenAI API credentials with access to the configured chat and embedding models
- Pinecone account and index (serverless or pod)
- Optional: Conda for `environment.yml`, or any other virtual environment manager
- Optional: LangSmith account for tracing (`LANGCHAIN_*` variables)

---

## Setup

### 1. Create and activate an environment

Option A - Conda
```bash
conda env create -f environment.yml
conda activate sleep-assistant
```

Option B - Python venv
```bash
python -m venv .venv
.\.venv\Scripts\activate        # Windows
source .venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
```
This installs the runtime dependencies listed in `requirements.txt`.

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill in the required values. Minimum variables include:

- `OPENAI_API_KEY` - API key for OpenAI.
- `OPENAI_BASE_URL` - Base URL for the OpenAI-compatible endpoint.
- `CHAT_MODEL` - Chat model name (defaults to `gpt-4o-mini`).
- `EMBEDDING_MODEL` - Embedding model name (defaults to `text-embedding-3-small`).
- `PINECONE_API_KEY` - Pinecone access token.
- `PINECONE_INDEX_NAME` - Target Pinecone index.
- `PINECONE_INDEX_HOST` / `PINECONE_HOST_NAME` / `PINECONE_INDEX_URL` - One of these for non-serverless indexes.

Optional extras:

- `LANGCHAIN_TRACING_V2`, `LANGCHAIN_ENDPOINT`, `LANGCHAIN_API_KEY` - Enable LangSmith telemetry.

Keep the `.env` file out of version control.

### 3. Verify the installation

```bash
python -m pip check
python -m fastapi --help  # optional sanity check
```

---

## Run the assistant

### CLI chat

```bash
python scripts/run_chatbot.py
```

You will be dropped into an interactive session. Messages are routed exactly as the API would handle them.

### FastAPI service

```bash
python scripts/run_api.py --reload --port 8001
```

Sample request:

```bash
curl -X POST http://127.0.0.1:8001/chat ^
     -H "Content-Type: application/json" ^
     -d "{\"message\": \"Why do I wake up in the middle of the night?\"}"
```

On Unix shells replace the line continuation character `^` with `\`.

---

## Project structure

```plaintext
.
|-- scripts/
|   |-- run_api.py            # FastAPI launcher
|   |-- run_chatbot.py        # CLI entrypoint
|-- src/
|   |-- sleep_assistant/
|       |-- api/              # FastAPI app, routers, schemas, validators
|       |-- config/           # Environment helpers and settings
|       |-- graph/            # LangGraph wiring (nodes, prompts, state, edges)
|       |-- services/         # LLM and vector store factories
|       |-- cli.py            # CLI runner utilities
|-- .env.example              # Template for required secrets
|-- environment.yml           # Conda environment specification
|-- requirements.txt          # Pip requirements for virtualenv installs
|-- README.md
```

---

## Troubleshooting

- Router misclassification - Ensure the router prompt in `src/sleep_assistant/graph/prompts/router.py` matches the latest specification; escape braces for literal JSON examples.
- Pinecone connectivity errors - Double-check index name, region or host, and VPC access settings. Serverless indexes generally require only the name.
- Model errors - The assistant depends on both chat and embedding models. Confirm the environment variables align with your OpenAI deployment.
- LangGraph state issues - Clear the in-memory session by restarting the process; persistent storage is not included in this starter.

---

## Next steps

- Add evaluation via LangSmith and exported traces.
- Wire in persistent conversation storage or retrieval augmentation beyond Pinecone.
- Extend the graph with new specialist nodes (for example nutrition or mindfulness) by following the patterns in `src/sleep_assistant/graph/nodes/`.
