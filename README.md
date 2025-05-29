# Local RAG POC

A local Retrieval-Augmented Generation (RAG) system using Docker for running entirely on your PC. This system provides:

- **PostgreSQL** with `pgvector` extension for efficient vector similarity search
- **Python encoder** that chunks and embeds markdown/source code files using Sentence Transformers
- **Ollama** serving a lightweight local LLM (e.g., `gemma:2b`)

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have the following installed:
- **Docker** and **Docker Compose** (v2.x recommended)
- **Python 3.10+** with pip
- At least **6-8 GB RAM** and **2-4 CPU cores**

### 2. Clone and Setup
```bash
git clone <your-repo-url>
cd rag-poc
```

### 3. Add Your Knowledge Base
Place your documents in the `data/` folder:
```bash
# Example: Add some sample files
echo "# Welcome to RAG\nThis is a sample document for testing." > data/sample.md
echo "# Another Doc\nThis contains more information about the system." > data/guide.md
```

### 4. Install Python Dependencies
```bash
pip install sentence-transformers psycopg2-binary requests
```

### 5. Start the System
```bash
docker compose up --build
```

**What happens:**
1. PostgreSQL starts with pgvector extension
2. Encoder service processes your documents and creates embeddings
3. Ollama downloads and serves the gemma:2b model

### 6. Query Your Knowledge Base
Once all services are running (wait for "encoder_1 exited with code 0"):
```bash
python rag.py "What is this system about?"
```

---

## 🧠 How It Works

```
Your Question → Sentence Transformer → Vector Search (PostgreSQL) →
   → Retrieve Similar Chunks → LLM Prompt → Generated Answer
```

1. **Document Processing**: Files in `data/` are chunked and embedded using MiniLM
2. **Vector Storage**: Embeddings stored in PostgreSQL with pgvector for fast similarity search
3. **Query Processing**: Your question is embedded and matched against stored chunks
4. **Answer Generation**: Retrieved context is sent to Ollama's LLM for final answer

---

## 📁 Project Structure

```
rag-poc/
├── data/                   # 📁 Your knowledge base files (.md, .py)
├── encoder/
│   ├── Dockerfile          # 🐳 Python environment for embedding
│   └── embed.py           # 🔧 Document processing script
├── pgvector/
│   └── Dockerfile         # 🐳 PostgreSQL with vector extension
├── docker-compose.yml     # 🐳 Service orchestration
├── rag.py                 # 🔍 Main query interface
├── requirements.txt       # 📦 Python dependencies
└── README.md             # 📖 This file
```

---

## 🔧 Configuration & Customization

### Change the LLM Model
Edit `rag.py` line 31 to use different models:
```python
"model": "mistral",     # or "llama2", "codellama", etc.
```

### Adjust Chunk Settings
Modify `encoder/embed.py` line 28:
```python
def chunk_text(text, chunk_size=500, overlap=50):  # Experiment with these values
```

### Add More File Types
Extend `encoder/embed.py` to support PDFs, DOCX, etc.:
```python
# Add to the file type check:
if filepath.suffix not in [".md", ".py", ".txt", ".pdf"]:
```

---

## 🚨 Troubleshooting

### Service Won't Start
```bash
# Check Docker status
docker compose ps

# View logs for specific service
docker compose logs pgvector
docker compose logs encoder
docker compose logs ollama
```

### "Connection Refused" Error
- Ensure all services are running: `docker compose ps`
- Wait for Ollama to download the model (first run takes time)
- Check if ports 5432 and 11434 are available

### Out of Memory
- Reduce chunk size in `embed.py`
- Use a smaller model like `gemma:2b` instead of larger ones
- Ensure Docker has enough memory allocated (6GB+)

### No Documents Found
- Verify files are in `data/` folder
- Check encoder logs: `docker compose logs encoder`
- Ensure file extensions are `.md` or `.py`

---

## 📊 Performance Notes

| Component | Resource Usage | Notes |
|-----------|---------------|-------|
| PostgreSQL | ~200MB RAM | Scales with document count |
| Encoder | ~1GB RAM | Temporary, exits after processing |
| Ollama | ~4GB RAM | Persistent, loads model in memory |
| **Total** | **~6GB RAM** | Plus your documents |

**First Run**: May take 5-10 minutes to download the LLM model
**Subsequent Runs**: ~30 seconds to start all services

---

## 🛠 Development & Production

### For Development
- Add more sophisticated chunking strategies
- Implement reranking for better retrieval
- Add support for more file formats
- Build a web UI with FastAPI + React

### For Production
- Add authentication and rate limiting
- Implement proper error handling and logging
- Use managed PostgreSQL service
- Add monitoring and health checks

---

## 💡 Tips & Best Practices

- **Documents**: Keep files focused and well-structured for better chunking
- **Queries**: Be specific in your questions for better results
- **Models**: Start with `gemma:2b`, upgrade to larger models if needed
- **Chunks**: Smaller chunks = more precise, larger chunks = more context

---

## 📜 License

MIT License - Feel free to use and modify for your projects!

---

*Built with ❤️ for local AI experimentation*
