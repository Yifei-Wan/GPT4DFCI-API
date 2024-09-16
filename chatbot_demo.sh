#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Function to display usage
usage() {
    echo "Usage: $0 -q <question>"
    exit 1
}

# Parse arguments
while getopts ":q:" opt; do
    case $opt in
        q)
            QUESTION=$OPTARG
            ;;
        *)
            usage
            ;;
    esac
done

# Check if question is provided
if [ -z "$QUESTION" ]; then
    usage
fi

# Activate the chatbot virtual environment
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
    echo "Activated the DFCI chatbot environment."
else
    echo "Virtual environment activation script not found. Exiting."
    exit 1
fi

# Set environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "Environment variables set from .env file."
else
    echo ".env file not found. Exiting."
    exit 1
fi

# Run chatbot with the provided question
echo -e
echo "--------------------------------------------------"
echo -e
python query_vector_database.py -q "$QUESTION"