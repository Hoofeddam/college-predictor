# College Predictor - Setup

## Python environment

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
## Install CPU-only PyTorch

This project uses Sentence Transformers for embeddings and runs inference on CPU.

Install the CPU-only PyTorch build:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
## Install project dependencies

```bash
pip install -r requirements.txt
## Embedding model

The project uses:

`BAAI/bge-small-en-v1.5`

The model is downloaded automatically from Hugging Face the first time it is used.

## Verify the embedding system

```bash
python -c "from rag.embedder import create_embedding; x=create_embedding('This is a test'); print('EMBEDDING OK:', len(x))"
Expected:

EMBEDDING OK: 384
