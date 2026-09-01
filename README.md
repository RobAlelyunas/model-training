# Project Setup & Quickstart

Welcome! This is a project that provides a UI to iteratively train a behavioral layer into your own LLM model. 

## Apple Silicon is Required
The project requires an Apple Macintosh running on a Apple Silicon chip.  It makes use of mlx suite of methods to efficiently train and query models from the ui.  To check your system, run the check_system.sh script provided if you are not sure.

## To Run as installed app
Go to project releases and download the latest release DMG.  

## To Run as python project

[clone project]
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.main

