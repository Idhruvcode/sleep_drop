# Sleep Assistant Service

The Sleep Assistant is a LangGraph-powered multi-agent experience that routes every user message to the right expertise. It distinguishes casual greetings from sleep-focused questions, enriches sleep conversations with MongoDB Atlas Vector Search context retrieval, and serves responses through a CLI helper and a FastAPI endpoint.

---

## Features

- FastAPI service for real-time chat over HTTP on port 8001.
- CLI companion (`scripts/run_chatbot.py`) for local conversational testing.
- LangGraph orchestration with an intent router, general chat node, and sleep-specialist node.
- Sleep knowledge base powered by MongoDB Atlas Vector Search and OpenAI embeddings.
- Environment-driven configuration with a simple `.env` workflow.
- Optional observability through LangSmith and structured logging.

## Conversation Flow

1. The router prompt classifies each incoming message as either `general` or `sleep`.
2. Greetings and small talk are answered by the general node via an LLM tuned for casual conversation.
3. Sleep-related questions trigger MongoDB vector retrieval, combining matched snippets with a dedicated sleep prompt before responding.

---

## Prerequisites

- Python 3.11 (CPython recommended)
- OpenAI API credentials with access to the configured chat and embedding models
- MongoDB Atlas cluster with an enabled vector search index
- Tesseract OCR binary (required if you ingest scanned PDFs with the included script)
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
- `MONGODB_URI` - Full MongoDB connection string (preferred).
- or `MONGODB_USERNAME`, `MONGODB_PASSWORD`, `MONGODB_CLUSTER_URL` - Provide these if you want the app to build the URI.
- `MONGODB_DBNAME` - Database containing your vectorized documents.
- `MONGODB_COLLECTION` - Collection used for vector search.
- `MONGODB_VECTOR_INDEX` - Atlas vector index name (defaults to `vector_index`).
- `MONGODB_EMBEDDING_FIELD` - Document field that stores embeddings (defaults to `embedding`).
- `MONGODB_VECTOR_CANDIDATES` - (Optional) Override the Atlas `numCandidates` setting for fine control.

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

### Streamlit app

Launch a lightweight UI with Streamlit once your environment variables are configured:

**From the project root directory:**

```bash
streamlit run streamlit_app.py
```

The app will start and automatically open in your default web browser at `http://localhost:8501`. If it doesn't open automatically, navigate to that URL manually.

**Features:**
- Interactive chat interface for conversing with the Sleep Assistant
- Full conversation transcript with message history
- Sidebar showing session metrics (user turns, latest route)
- "Start new conversation" button to reset the session without restarting the server
- Display of knowledge sources (MongoDB Atlas snippets) that informed each response
- Relevance scores for retrieved documents

**Requirements:**
- Ensure your `.env` file is properly configured with OpenAI and MongoDB credentials
- All dependencies from `requirements.txt` must be installed (including `streamlit>=1.37`)

**Stopping the app:**
- Press `Ctrl+C` in the terminal where Streamlit is running

---

### Prepare the knowledge base (bring your own ingestion)

Populate the MongoDB collection referenced by `MONGODB_COLLECTION` with the documents you want the assistant to cite. A typical workflow is:

1. Extract text from your PDFs (PyMuPDF works well for digital text; fall back to Tesseract OCR for scanned pages).
2. Chunk each document and call `sleep_assistant.services.llm.build_embedder()` to generate OpenAI embeddings.
3. Insert documents into MongoDB with an `embedding` array plus metadata fields such as `text`, `source_document`, and `page_number`.
4. Create a MongoDB Atlas Vector Search index that targets the embedding field named in `MONGODB_EMBEDDING_FIELD`.

Once populated, the sleep node automatically queries this collection and surfaces the snippets with the highest similarity scores.

---

### Docker deployment

1. Ensure your `.env` file is populated with the required OpenAI and MongoDB credentials.
2. Build the image:
   ```bash
   docker build -t sleep-assistant .
   ```
3. Run the API service (port 8001) with the environment file mounted:
   ```bash
   docker run --env-file .env -p 8001:8001 sleep-assistant
   ```

Alternatively, you can use the included Compose file:
```bash
docker compose up --build
```
The Compose service loads variables from `.env` and exposes the API on `http://localhost:8001`.

---

## Project structure

```plaintext
.
|-- scripts/
|   |-- run_api.py            # FastAPI launcher
|   |-- run_chatbot.py        # CLI entrypoint
|-- src/
|   |-- ingest/               # PDF/OCR utilities for knowledge prep
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
- MongoDB connectivity errors - Double-check the URI (or username/password/cluster trio), ensure the database and collection exist, and confirm the vector index has finished building.
- Model errors - The assistant depends on both chat and embedding models. Confirm the environment variables align with your OpenAI deployment.
- LangGraph state issues - Clear the in-memory session by restarting the process; persistent storage is not included in this starter.

---

## Next steps

- Add evaluation via LangSmith and exported traces.
- Wire in persistent conversation storage or retrieval augmentation beyond MongoDB vector search.
- Extend the graph with new specialist nodes (for example nutrition or mindfulness) by following the patterns in `src/sleep_assistant/graph/nodes/`.
