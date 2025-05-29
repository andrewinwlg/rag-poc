# Troubleshooting Guide

This guide helps you resolve common issues with the local RAG system.

## Docker Issues

### Services Won't Start

**Problem**: Docker containers fail to start or exit immediately.

**Solutions**:
1. Check Docker status: `docker compose ps`
2. View logs: `docker compose logs <service-name>`
3. Ensure Docker has enough memory (6GB+ recommended)
4. Check if ports 5432 and 11434 are available

### Out of Memory Errors

**Problem**: Services crash due to insufficient memory.

**Solutions**:
- Increase Docker memory allocation
- Use smaller models (e.g., `gemma:2b` instead of larger models)
- Reduce chunk size in embedding process
- Close other memory-intensive applications

## Database Issues

### Connection Refused

**Problem**: Cannot connect to PostgreSQL database.

**Solutions**:
1. Ensure pgvector service is running
2. Wait for database initialization (first run takes time)
3. Check database logs: `docker compose logs pgvector`
4. Verify environment variables are correct

### No Documents Found

**Problem**: RAG system reports no documents in database.

**Solutions**:
1. Verify files are in `data/` folder
2. Check supported file extensions (.md, .py, .txt)
3. Review encoder logs: `docker compose logs encoder`
4. Ensure encoder service completed successfully

## Ollama Issues

### Model Download Fails

**Problem**: Ollama cannot download the specified model.

**Solutions**:
- Check internet connection
- Try a different model (e.g., `mistral` instead of `gemma:2b`)
- Manually pull model: `docker exec -it <ollama-container> ollama pull gemma:2b`
- Increase timeout in docker-compose.yml

### LLM Responses Are Slow

**Problem**: Queries take a long time to complete.

**Solutions**:
- Use smaller models for faster responses
- Reduce the number of retrieved chunks (`--limit` parameter)
- Ensure adequate CPU resources
- Consider using GPU if available

## Query Issues

### Poor Answer Quality

**Problem**: RAG system provides irrelevant or incorrect answers.

**Solutions**:
- Use more specific questions
- Adjust chunk size and overlap in `embed.py`
- Increase number of retrieved chunks
- Try different LLM models
- Improve document structure and content

### No Relevant Context Found

**Problem**: System cannot find relevant information for queries.

**Solutions**:
1. Verify documents contain relevant information
2. Try different phrasing of the question
3. Check if embeddings were created correctly
4. Increase similarity search limit

## Performance Optimization

### Slow Embedding Process

**Solutions**:
- Reduce chunk size
- Process fewer files at once
- Use a machine with better CPU
- Consider using GPU acceleration

### Slow Query Response

**Solutions**:
- Create database indexes on frequently queried fields
- Use smaller vector dimensions (if modifying the model)
- Optimize PostgreSQL configuration
- Cache frequently used embeddings

## General Tips

1. **Check logs first**: Most issues can be diagnosed from service logs
2. **Resource monitoring**: Keep an eye on CPU and memory usage
3. **Incremental testing**: Test with small datasets first
4. **Clean restarts**: Sometimes `docker compose down && docker compose up --build` helps
5. **Patience**: First runs take longer due to model downloads and setup

## Getting Help

If you're still experiencing issues:
1. Check the GitHub repository for known issues
2. Review the system requirements
3. Consider posting detailed logs when seeking help
4. Try with minimal configuration first 