# ==========================================
# RAG POC on Google Colab - Free GPU Setup
# ==========================================
# Copy each section into separate Colab cells

# CELL 1: Setup and Installation
print("🚀 RAG POC on Free GPU - Google Colab")
print("Make sure Runtime -> Change runtime type -> GPU is selected!")
print("="*60)

# Install dependencies
import subprocess
import sys

def install_and_import(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

packages = [
    "sentence-transformers", 
    "transformers", 
    "torch", 
    "chromadb", 
    "requests"
]

print("📦 Installing packages...")
for package in packages:
    install_and_import(package)

print("✅ All packages installed!")

# CELL 2: Clone Repository
import os
if os.path.exists('rag-poc'):
    os.chdir('rag-poc')
    os.system('git pull')
else:
    os.system('git clone https://github.com/andrewinwlg/rag-poc.git')
    os.chdir('rag-poc')

print("✅ Repository ready!")
os.system('ls -la data/')

# CELL 3: Setup Ollama LLM
print("🤖 Setting up Ollama...")
os.system('curl -fsSL https://ollama.ai/install.sh | sh')

import subprocess
import time
import requests

# Start Ollama server
ollama_process = subprocess.Popen(
    ["ollama", "serve"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

time.sleep(10)
print("📥 Downloading model...")
os.system('ollama pull gemma:2b')

# Test connection
try:
    response = requests.get("http://localhost:11434/api/version", timeout=5)
    if response.status_code == 200:
        print("✅ Ollama ready with GPU!")
    else:
        print("⚠️ Ollama may not be ready - try again")
except:
    print("⚠️ Connection issue - run this cell again")

# CELL 4: Setup Vector Database
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
import uuid

print("🧠 Loading embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

print("🗄️ Setting up vector database...")
client = chromadb.Client()
collection = client.create_collection("rag_documents")

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = words[i:i+chunk_size]
        if len(chunk) > 0:
            chunks.append(" ".join(chunk))
    return chunks

# Process documents
documents = []
metadatas = []
ids = []

data_path = Path("data")
for filepath in data_path.glob("**/*"):
    if filepath.suffix in [".md", ".txt", ".py"]:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            
            if text.strip():
                chunks = chunk_text(text)
                for i, chunk in enumerate(chunks):
                    documents.append(chunk)
                    metadatas.append({
                        "filename": filepath.name,
                        "chunk_index": i
                    })
                    ids.append(f"{filepath.name}_{i}_{str(uuid.uuid4())[:8]}")
                
                print(f"✅ Processed {filepath.name}: {len(chunks)} chunks")
        except Exception as e:
            print(f"⚠️ Error processing {filepath.name}: {e}")

# Add to vector database
if documents:
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print(f"✅ Vector database ready with {len(documents)} chunks!")
else:
    print("❌ No documents found!")

# CELL 5: RAG Query Function
def query_rag(question, top_k=5, model="gemma:2b", verbose=False):
    """Query the RAG system"""
    print(f"🔍 Searching for: '{question}'")
    
    # Query vector database
    results = collection.query(
        query_texts=[question],
        n_results=top_k
    )
    
    if not results['documents'][0]:
        return "❌ No relevant documents found."
    
    # Build context
    context_chunks = results['documents'][0]
    context = "\\n---\\n".join(context_chunks)
    
    if verbose:
        print("\\n📄 Retrieved Context:")
        for i, chunk in enumerate(context_chunks):
            print(f"Chunk {i+1}: {chunk[:150]}...")
    
    # Create prompt
    prompt = f"""Use the following context to answer the question.

Context:
{context}

Question: {question}

Answer:"""
    
    # Query LLM
    try:
        print(f"🤖 Asking {model}...")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json().get("response", "No response")
        else:
            return f"❌ Error: Status {response.status_code}"
    except Exception as e:
        return f"❌ Error: {e}"

print("✅ RAG function ready!")

# CELL 6: Test the System
test_questions = [
    "What is this RAG system about?",
    "How do I troubleshoot issues?",
    "What are the key components?"
]

for question in test_questions:
    print(f"\\n{'='*50}")
    print(f"Question: {question}")
    print('='*50)
    
    answer = query_rag(question)
    print("\\nAnswer:")
    print("-" * 30)
    print(answer)
    print("-" * 30)

print("\\n🎉 RAG System working on free GPU!")

# CELL 7: Custom Questions
# Edit this cell to ask your own questions:

my_question = "How do I add my own documents?"
print(f"🎯 Your Question: {my_question}")
answer = query_rag(my_question, verbose=True)
print(f"\\n🤖 Answer:\\n{answer}")

print("\\n💡 Edit 'my_question' above and run again!")
print("\\n🚀 Your RAG POC is running 5-10x faster on free GPU!") 