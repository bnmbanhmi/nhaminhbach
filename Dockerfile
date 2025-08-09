# Use an official, slim Python base image
FROM python:3.11-slim

# Set a working directory inside the container
WORKDIR /app

# Install system dependencies for Playwright and Chromium
# This is done before installing Python packages to leverage Docker's layer caching
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libatspi2.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements.txt file to leverage Docker's layer caching
COPY packages/scraper/requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install the Playwright browser binaries
RUN playwright install chromium

# Copy the entire scraper source code into the container
COPY packages/scraper/ ./scraper/

# Define the entrypoint for the container
ENTRYPOINT ["python", "-m", "scraper.main"]
