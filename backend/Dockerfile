FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download FinBERT model to avoid download during runtime
# This adds ~450MB to image size but ensures faster startup
RUN python3 -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; \
    model_name = 'yiyanghkust/finbert-tone'; \
    print('Downloading FinBERT model...'); \
    AutoTokenizer.from_pretrained(model_name); \
    AutoModelForSequenceClassification.from_pretrained(model_name); \
    print('FinBERT model cached successfully')"

# Copy application code
COPY . .

# Create cache directory for HuggingFace transformers
RUN mkdir -p /app/.cache

# Set HuggingFace cache directory
ENV TRANSFORMERS_CACHE=/app/.cache
ENV HF_HOME=/app/.cache

# Expose port
EXPOSE 8000

# Start server (skip migrations if no DB available)
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000
