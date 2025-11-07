FROM python:3.11-slim

# Ensure Python runs in unbuffered mode and does not write .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy application source
COPY src ./src
COPY scripts ./scripts
COPY README.md .

# Allow src to be importable as a package
ENV PYTHONPATH=/app/src

# Expose FastAPI's default listening port
EXPOSE 8001

# Default command launches the FastAPI service
CMD ["uvicorn", "sleep_assistant.api.main:app", "--host", "0.0.0.0", "--port", "8001"]
