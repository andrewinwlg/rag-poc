import os
import time
import psycopg2
from sentence_transformers import SentenceTransformer
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def wait_for_db(max_retries=30, retry_interval=2):
    """Wait for database to be ready with connection retries."""
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB", "ragdb"),
                user=os.getenv("POSTGRES_USER", "rag"),
                password=os.getenv("POSTGRES_PASSWORD", "ragpass"),
                host=os.getenv("POSTGRES_HOST", "pgvector"),
                port=5432
            )
            conn.close()
            logger.info("Database connection successful!")
            return True
        except psycopg2.OperationalError as e:
            logger.info(f"Waiting for database... (attempt {attempt + 1}/{max_retries})")
            time.sleep(retry_interval)
    
    logger.error("Could not connect to database after maximum retries")
    return False

def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = words[i:i+chunk_size]
        if len(chunk) > 0:  # Avoid empty chunks
            chunks.append(" ".join(chunk))
    return chunks

def main():
    logger.info("Starting document embedding process...")
    
    # Wait for database to be ready
    if not wait_for_db():
        return
    
    # Connect to database
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "ragdb"),
            user=os.getenv("POSTGRES_USER", "rag"),
            password=os.getenv("POSTGRES_PASSWORD", "ragpass"),
            host=os.getenv("POSTGRES_HOST", "pgvector"),
            port=5432
        )
        cur = conn.cursor()
        logger.info("Connected to database successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return

    # Clear existing documents (for fresh start)
    try:
        cur.execute("DELETE FROM documents;")
        conn.commit()
        logger.info("Cleared existing documents")
    except Exception as e:
        logger.error(f"Failed to clear documents: {e}")
        return

    # Initialize the sentence transformer model
    logger.info("Loading sentence transformer model...")
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return

    # Process documents
    data_path = Path("/app/data")
    if not data_path.exists():
        logger.error("Data directory not found")
        return

    processed_files = 0
    total_chunks = 0
    
    for filepath in data_path.glob("**/*"):
        if not filepath.is_file() or filepath.suffix not in [".md", ".py", ".txt"]:
            continue
            
        try:
            logger.info(f"Processing file: {filepath.name}")
            
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            
            if not text.strip():
                logger.warning(f"Empty file skipped: {filepath.name}")
                continue
            
            chunks = chunk_text(text)
            logger.info(f"Created {len(chunks)} chunks from {filepath.name}")
            
            if chunks:
                embeddings = model.encode(chunks)
                
                for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                    cur.execute(
                        "INSERT INTO documents (filename, chunk_index, content, embedding) VALUES (%s, %s, %s, %s)",
                        (filepath.name, i, chunk, emb.tolist())
                    )
                
                conn.commit()
                processed_files += 1
                total_chunks += len(chunks)
                logger.info(f"Successfully processed {filepath.name}")
            
        except Exception as e:
            logger.error(f"Error processing {filepath.name}: {e}")
            continue

    logger.info(f"Embedding process completed!")
    logger.info(f"Processed {processed_files} files with {total_chunks} total chunks")
    
    # Verify the data was inserted
    try:
        cur.execute("SELECT COUNT(*) FROM documents;")
        count = cur.fetchone()[0]
        logger.info(f"Verified: {count} documents stored in database")
    except Exception as e:
        logger.error(f"Failed to verify document count: {e}")
    
    conn.close()
    logger.info("Database connection closed")

if __name__ == "__main__":
    main() 