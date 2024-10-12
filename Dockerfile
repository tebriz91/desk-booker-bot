# Base Python image
FROM python:3.11.5-slim-bullseye as base

# Environment variables for Python
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install UV using pip
RUN pip install uv

# Set the working directory in the Docker container
WORKDIR /app

# Copy only pyproject.toml to cache dependencies
COPY pyproject.toml ./

# Install dependencies from pyproject.toml
RUN uv install

# Copy the rest of the project
COPY . .

# Command to run the application
CMD ["uv", "run", "python", "app/bot.py"]
