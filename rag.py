#!/usr/bin/env python3
"""
RAG Query Interface - Ask questions about your documents
Usage: python rag.py "Your question here"
"""

import sys
import argparse
import psycopg2
from sentence_transformers import SentenceTransformer
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Ask questions about your documents using RAG')
    parser.add_argument('query', help='Your question or query')
    parser.add_argument('--model', default='gemma:2b', help='LLM model to use (default: gemma:2b)')
    parser.add_argument('--limit', type=int, default=5, help='Number of chunks to retrieve (default: 5)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    return parser.parse_args()

def connect_to_database():
    """Connect to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname="ragdb",
            user="rag",
            password="ragpass",
            host="localhost",
            port=5432
        )
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection failed: {e}")
        logger.info("Make sure the PostgreSQL service is running: docker compose ps")
        return None

def retrieve_relevant_chunks(query, limit=5, verbose=False):
    """Retrieve relevant document chunks using vector similarity."""
    logger.info("Loading sentence transformer model...")
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return []
    
    logger.info("Encoding query...")
    query_vector = model.encode([query])[0].tolist()
    
    logger.info("Connecting to database...")
    conn = connect_to_database()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        
        # Check if we have any documents
        cur.execute("SELECT COUNT(*) FROM documents;")
        doc_count = cur.fetchone()[0]
        
        if doc_count == 0:
            logger.warning("No documents found in database. Run the encoder service first.")
            return []
        
        logger.info(f"Searching through {doc_count} document chunks...")
        
        # Retrieve similar chunks using cosine distance
        cur.execute("""
            SELECT content, filename, chunk_index, 
                   (embedding <#> %s) as distance
            FROM documents
            ORDER BY embedding <#> %s
            LIMIT %s;
        """, (query_vector, query_vector, limit))
        
        results = cur.fetchall()
        
        if verbose:
            logger.info(f"Retrieved {len(results)} relevant chunks:")
            for i, (content, filename, chunk_idx, distance) in enumerate(results):
                logger.info(f"  {i+1}. {filename}[{chunk_idx}] (distance: {distance:.3f})")
        
        return [result[0] for result in results]  # Return just the content
        
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        return []
    finally:
        conn.close()

def query_llm(prompt, model_name="gemma:2b"):
    """Send prompt to Ollama LLM and get response."""
    try:
        logger.info(f"Querying {model_name} model...")
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False
            },
            timeout=120  # 2 minute timeout
        )
        
        if response.status_code == 200:
            return response.json().get("response", "No response received")
        else:
            logger.error(f"LLM request failed with status {response.status_code}")
            return f"Error: LLM service returned status {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama service")
        logger.info("Make sure Ollama is running: docker compose ps")
        return "Error: Cannot connect to LLM service. Make sure Ollama is running."
    except requests.exceptions.Timeout:
        logger.error("LLM request timed out")
        return "Error: LLM request timed out. Try a simpler question."
    except Exception as e:
        logger.error(f"LLM request failed: {e}")
        return f"Error: {e}"

def main():
    """Main function to run the RAG query."""
    args = parse_arguments()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    query = args.query
    logger.info(f"Processing query: '{query}'")
    
    # Retrieve relevant chunks
    relevant_chunks = retrieve_relevant_chunks(query, args.limit, args.verbose)
    
    if not relevant_chunks:
        print("❌ No relevant documents found. Make sure you have:")
        print("   1. Added documents to the data/ folder")
        print("   2. Run 'docker compose up' to process them")
        return
    
    # Build context from retrieved chunks
    context = "\n---\n".join(relevant_chunks)
    
    # Create prompt for LLM
    prompt = f"""Use the following context to answer the question. Be specific and helpful.
If you cannot answer based on the context, say so clearly.

Context:
{context}

Question: {query}

Answer:"""
    
    if args.verbose:
        print("\n" + "="*50)
        print("CONTEXT SENT TO LLM:")
        print("="*50)
        print(context)
        print("="*50 + "\n")
    
    # Query the LLM
    answer = query_llm(prompt, args.model)
    
    # Display result
    print("\n🤖 Answer:")
    print("-" * 40)
    print(answer)
    print()

if __name__ == "__main__":
    main() 