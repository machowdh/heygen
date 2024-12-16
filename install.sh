#!/bin/bash

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Ensure Redis is installed
if ! command_exists redis-server; then
  echo "Redis is not installed. Installing Redis..."
  sudo apt-get update && sudo apt-get install -y redis-server
else
  echo "Redis is already installed."
fi

# Ensure Python dependencies are installed
if ! command_exists uv; then
  echo "Installing uv and syncing dependencies..."
  
  curl -LsSf https://astral.sh/uv/install.sh | sh
  
  uv sync
else
  echo "uv is already installed. Syncing dependencies..."
  uv sync
fi
