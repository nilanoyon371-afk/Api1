#!/bin/bash

# 1. Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# 2. Install Playwright browsers
echo "Installing Playwright browsers..."
python -m playwright install --with-deps
