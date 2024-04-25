#!/bin/bash

# Install virtualenv package
pip install virtualenv

# Create Python virtual environment
python3 -m virtualenv venv

# Activate Python virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Run Python module
python -m src.main
