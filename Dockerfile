# Stage 1: Builder
FROM python:3.10-slim-buster AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN pip install --upgrade pip

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final Image
FROM python:3.10-slim-buster

# Set working directory
WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy the application code
COPY . .

# Expose the port that Uvicorn will run on
EXPOSE 8000

# Define environment variable for FastAPI app
ENV PYTHONPATH=/app

# Run the Uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
