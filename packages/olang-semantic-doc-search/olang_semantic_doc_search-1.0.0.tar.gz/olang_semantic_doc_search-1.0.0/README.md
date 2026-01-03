# O-lang Semantic Document Search (Python)

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![O-lang Compatible](https://img.shields.io/badge/olang-compatible-brightgreen)

Python implementation of the semantic document search resolver for **O-lang workflows**. Enables natural language search across document collections using state-of-the-art embeddings.

## 🚀 Features

- **O-lang Protocol Compliant**: Works seamlessly with O-lang kernel
- **Local Embeddings**: Uses `all-MiniLM-L6-v2` (384-dim) for privacy and cost savings
- **pgvector Support**: Optional PostgreSQL + pgvector integration for persistence
- **In-Memory Fallback**: Works without database for simple use cases
- **Production Ready**: Built-in error handling, timeouts, and validation
- **Cross-Platform**: Runs on Windows, macOS, and Linux

## 📥 Installation

### Basic Installation
```bash
pip install olang-semantic-doc-search