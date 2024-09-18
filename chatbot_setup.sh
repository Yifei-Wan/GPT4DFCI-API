#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Sync the vector database from S3
S3_BUCKET="s3://rag-vector-databases/chromadb"
LOCAL_DIR="chromadb"
if aws s3 sync "$S3_BUCKET" "$LOCAL_DIR"; then
    echo "Successfully synced vector database from $S3_BUCKET to $LOCAL_DIR."
else
    echo "Failed to sync vector database. Exiting."
    exit 1
fi

# Azure login
az login --allow-no-subscriptions

