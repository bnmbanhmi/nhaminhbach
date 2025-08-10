# 1. Base Image: Use a standard, slim Python image.
# python:3.11-slim is a good choice for Cloud Functions.
FROM python:3.11-slim

# 2. Set Environment Variables
# APP_HOME is the conventional directory for applications.
# PYTHONUNBUFFERED ensures that print statements are sent straight to the terminal without being buffered first.
ENV APP_HOME /app
ENV PYTHONUNBUFFERED True
WORKDIR $APP_HOME

# 3. Install System-level Dependencies
# - libpq-dev: Contains header files needed to build PostgreSQL client libraries like pg8000 or asyncpg.
# - gcc: The GNU Compiler Collection, needed to compile C extensions that some Python packages rely on.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy and Install Python Requirements
# Copying requirements.txt first allows Docker to cache this layer.
# The layer will only be rebuilt if requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code
# This includes main.py and any other modules.
COPY . .

# No ENTRYPOINT or CMD is needed.
# Google Cloud Functions provides the entrypoint that runs your function
# using the Functions Framework based on the function signature in your code.
