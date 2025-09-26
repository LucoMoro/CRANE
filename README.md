# CRANE – Code Review AI Network Engine (Master Thesis Project)


![Python](https://img.shields.io/badge/Python-3.12.9-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Status](https://img.shields.io/badge/status-research--project-yellow)
![Dependencies](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen)
![Made with](https://img.shields.io/badge/Made%20with-LLMs-red)
[![DOI](https://zenodo.org/badge/885493473.svg)](https://doi.org/10.5281/zenodo.15518674)

CRANE is a research-driven system designed to explore the potential of Large Language Models (LLMs) in automating and enhancing the code review process through multi-agent collaboration. At its core, CRANE transforms the traditional code review workflow into a network of LLM agents that engage in structured conversations, each playing a specialized role in reviewing, critiquing, and ultimately resolving code review comments (CRs).

This project investigates a novel approach to prompt engineering where LLM agents not only analyze code and comments but also communicate with each other, mimicking a team of human reviewers. Their dialogue is then synthesized into actionable feedback that another LLM agent or a human can use to revise or improve the original code.

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/LucoMoro/CRANE
cd CRANE
```

### 2. Install Dependencies 
Make sure you have Python installed (preferably 3.12.9), then:

## On Ubuntu/Linux and macOS
Important: Before installing, open requirements.txt and remove the following line: 
```bash
pywin32==310
```
This package is Windows-only and will cause installation errors on Linux-based systems. Then:

```bash
python -m pip install -r requirements.txt
```

## On Windows
```bash
python -r requirements.txt
```


### 3. Configure Environment Variables
Create a .env file in the root of the project and add the following variables:
```bash
HUGGINGFACE_API_KEY=your_huggingface_api_key
OPENAI_API_KEY=your_openai_api_key
PINECONE_KEY=your_pinecone_key
BASE_PATH=./conversations
DATASET_PATH=./dataset
```

### 4. Running CRANE
A sample Change Request (CR) has already been included in the dataset folder.  
This allows you to quickly test whether the model and environment are working correctly before adding your own CRs.

## On Ubuntu/Linux and macOS
Ensure model paths in the code do not include "../" — update them to be relative (e.g. "models/..." instead of "../models/..."). To run the project:
```bash
python3 -m network.main
```

## On Windows
You can keep "../" in model paths if they work for you. To run the project
```bash
python main.py
```

---

### Project Structure 

```bash
crane/
├── agents/              # Code for individual LLM agents
├── network/             # Multi-agent coordination logic
├── conversations/       # Saved agent conversations and interactions
├── dataset/             # Folder containing the CRs
│   ├── snippets/        # CRs' code snippets
│   └── tasks_description/ # CR's Task descriptions
├── utils/               # Helper functions
├── prompts/             # Prompts used by the LLMs
├── .env                 # Environment variables (not committed)
├── requirements.txt     # Python dependencies
```
