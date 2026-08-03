# Project Setup & Quickstart

Welcome! This is a project that provides convenient methods and a UI to iteratively train a behavioral layer into your own LLM model. Follow these steps to set up your environment, download the base model, and launch the application.

## 1. Clone the Repository
Clone the project repository to your local machine:

git clone https://github.com/RobAlelyunas/model-training.git
cd model-training


## 2. Run System Check
This project requires a Mac with Apple silicon, run the script to verify your hardware:

./check_system.sh

Note the amount of memory avaiable.


## 3. Set Up the Virtual Environment
Create a Python virtual environment and activate it:

python3 -m venv .venv
source .venv/bin/activate


## 4. Install Dependencies
Install all required packages (including mlx and the Hugging Face CLI tools) from the requirements file:

pip install -r requirements.txt


## 5. Download the Source Model

Download a source model. Smaller and quantized models take less memory and time, but the tradeoff is they are less deep and robust. You can use any source model, even a base model or an instruct model, but to get started, download the ralelyunas/Meta-Llama-3-8B-4bit from hugging face which will be fine with 6 gig of available memory. This is a quantized 4 bit base model.

Navigate into the models/sources directory and download the source model:

cd models/sources
huggingface-cli download ralelyunas/Meta-Llama-3-8B-4bit
cd ..


## 6. Run the Pipeline
To build your initial target model, return to the root directory and run the pipeline script. Since you have no training data yet, this safely copies your source model as a starting point and verifies your environment:

python -m src.pipeline


## 7. Start the UI
Once the output confirms there are no errors, start the user interface application:

python -m src.ui

# Explore the Toby personality

In the resources directory, there is a dataset with the Toby personality training data in it. To explore this dataset, run the pipeline with property overrides to build Toby as shown, then start up the UI as shown with the trained Toby model.

python -m src.pipeline --source_model Meta-Llama-3-8B-4bit --dataset_path resources/toby_dataset.jsonl --target_model Meta-Llama-3-8B-4bit-Toby

python -m src.main --source_model Meta-Llama-3-8B-4bit --dataset_path resources/toby_dataset.jsonl --target_model Meta-Llama-3-8B-4bit-Toby
