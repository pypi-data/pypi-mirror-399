# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

thefuckllm is a CLI tool that uses local LLMs to help answer command-line usage questions. It retrieves relevant context from man pages (with fallback to tldr and cheat.sh) and uses Qwen2.5-Coder-3B models via llama.cpp to generate answers.

## Commands

```bash
# Install dependencies (uses uv)
uv sync

# Run the main script
uv run python main.py

# Run the ollama chat script
uv run python ollama_chat.py '<your question>'
```

## Architecture

- **main.py**: Core application with two main components:
  - `ContextRetriever`: Retrieves and parses man pages, falls back to tldr/cheat.sh. Uses fastembed (BGE-small) for semantic search over man page sections.
  - `download_models()`: Downloads Qwen2.5-Coder-3B GGUF models to `~/.cache/thefuckllm/`
  - Uses llama-cpp-python for local inference with ChatML prompt format

- **ollama_chat.py**: Standalone streaming chat client for remote Ollama servers (OpenAI-compatible API)

## Key Dependencies

- `llama-cpp-python`: Local GGUF model inference
- `fastembed`: Text embeddings for semantic retrieval (BGE-small-en-v1.5)
- `huggingface-hub`: Model downloading
- `platformdirs`: Cross-platform cache directory management

## Model Details

Models are cached in the user cache directory (`platformdirs.user_cache_dir("thefuckllm")`):
- `qwen2.5-coder-3b-instruct-q4_k_m.gguf` - smaller quantization
- `qwen2.5-coder-3b-instruct-q8_0.gguf` - higher quality (default)
