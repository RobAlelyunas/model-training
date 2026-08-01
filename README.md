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


## 5. Download the Base Model
To get started, a 4 bit quantized, small, 2G base model is available from hugging face at ralelyunas/Llama-3.2-3B-4bit. You can use a larger model but generally speaking it should be a few gig smaller than your available memory. 

Navigate into the models/sources directory and download the source model:

cd models/sources
huggingface-cli download ralelyunas/Llama-3.2-3B-4bit
cd ..


## 6. Run the Pipeline
To build your initial target model, return to the root directory and run the pipeline script. Since you have no training data yet, this safely copies your source model as a starting point and verifies your environment:

python -m src.pipeline


## 7. Start the UI
Once the output confirms there are no errors, start the user interface application:

python -m src.main
