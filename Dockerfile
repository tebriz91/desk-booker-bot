# Base Python image
FROM python:3.11.5-slim-bullseye as base

# Environment variables for Python
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Poetry environment variables for version, no interaction, virtual envs creation, and cache directory
ENV POETRY_VERSION=1.8.2 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

# Install Poetry using the official installer script
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory in the Docker container
WORKDIR /app

# Copy only pyproject.toml and poetry.lock to cache dependencies
COPY poetry.lock pyproject.toml ./

# Install dependencies from pyproject.toml and poetry.lock
# Use the --no-root option if your project is a package and you don't want to install it
RUN poetry install $(test "$YOUR_ENV" = "production" && echo "--only=main") --no-interaction --no-ansi

# Copy the rest of the project
COPY . .

# Command to run the application, adjust as needed
CMD ["poetry", "run", "python", "app/bot.py"]