# Use an official, slim Python base image
FROM python:3.11-slim

# Set a working directory inside the container
WORKDIR /app

# Copy only the requirements.txt file to leverage Docker's layer caching
# This is done before installing dependencies to leverage Docker's layer caching
COPY packages/scraper/requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser binaries and system dependencies
RUN playwright install --with-deps chromium

# Copy the rest of the application code
# Assumes the scraper code is in packages/scraper and main.py is at the root
COPY packages/scraper/ .

# Set the command to run the scraper
# Assumes the main script is main.py
