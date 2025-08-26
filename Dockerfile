# Use official Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (if needed, e.g. gcc for some Python libs)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose FastAPI default port
EXPOSE 8000

# Run the app with uvicorn
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 & \
    sleep 3 && \
    echo 'Testing MCP server...' && \
    curl -i -X POST http://127.0.0.1:8000/mcp/ -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"ping\"}' || echo 'MCP test failed' && \
    fg"]
