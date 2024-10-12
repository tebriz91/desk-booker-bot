# Base Python image
FROM python:3.12-slim-bullseye

# Environment variables for Python
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gcc \
    build-essential \
    clang

# Copy the project into the image
ADD . /app

# Create a virtual environment
RUN python -m venv /app/.venv

# Activate the virtual environment and install dependencies
WORKDIR /app
RUN . /app/.venv/bin/activate && pip install --upgrade pip setuptools wheel

# Install dependencies from requirements.txt
COPY requirements.txt .
RUN . /app/.venv/bin/activate && pip install -r requirements.txt

# Copy the rest of the project
COPY . .

# Command to run the application
CMD ["/app/.venv/bin/python", "app/bot.py"]
