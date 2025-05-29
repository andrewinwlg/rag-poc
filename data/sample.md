# Welcome to the Local RAG System

This document provides an overview of our local Retrieval-Augmented Generation (RAG) system.

## What is RAG?

RAG combines the power of information retrieval with language generation. The system:

1. **Stores knowledge** in a vector database
2. **Retrieves relevant information** based on your queries
3. **Generates answers** using a local language model

## Key Components

### PostgreSQL with pgvector
- Stores document embeddings
- Enables fast similarity search
- Handles vector operations efficiently

### Sentence Transformers
- Converts text to embeddings
- Uses the MiniLM model for efficiency
- Creates 384-dimensional vectors

### Ollama
- Serves local language models
- Supports various models like Gemma, Mistral, and Llama
- Runs entirely on your local machine

## Benefits

- **Privacy**: All data stays on your machine
- **Speed**: No external API calls
- **Customization**: Easy to modify and extend
- **Cost-effective**: No API fees

## Getting Started

1. Add your documents to the `data/` folder
2. Run `docker compose up --build`
3. Query your knowledge base with `python rag.py "your question"`

## Tips for Better Results

- Use specific, well-formed questions
- Keep documents well-structured
- Experiment with different chunk sizes
- Try various LLM models for different use cases 