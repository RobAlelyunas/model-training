#!/bin/bash

# Runs the training pipeline that takes the working dataset (defined in properties.json)
# and creates a LoRA with it, fuses the LoRA back to the original base model, 
# quantizes the fused model, adds a chat template, and copies the 
# target to the distributable target.  The working dataset is any JSONL 
# file with each json object having two text entries, prompt and completion. 
# This is the training data.

set -e

cd "$(dirname "$0")"

echo "=== Starting AI Model Training Pipeline ==="

python3 -m src.pipeline

echo "=== Pipeline Script Finished ==="