#!/usr/bin/env python3
"""
Simple test script to verify RAG components are working
"""

import os
import sys
import time
import subprocess
import requests
from pathlib import Path

def test_docker():
    """Test if Docker is running and compose file is valid."""
    print("🐳 Testing Docker...")
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Docker is not running")
            return False
        
        # Check compose file
        if not Path("docker-compose.yml").exists():
            print("❌ docker-compose.yml not found")
            return False
            
        print("✅ Docker is ready")
        return True
    except FileNotFoundError:
        print("❌ Docker not installed")
        return False

def test_python_deps():
    """Test if Python dependencies are installed."""
    print("🐍 Testing Python dependencies...")
    required_packages = [
        "sentence_transformers",
        "psycopg2",
        "requests"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("✅ Python dependencies installed")
    return True

def test_data_files():
    """Test if data directory and files exist."""
    print("📁 Testing data directory...")
    
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ data/ directory not found")
        return False
    
    # Count supported files
    supported_files = list(data_dir.glob("**/*.md")) + list(data_dir.glob("**/*.py")) + list(data_dir.glob("**/*.txt"))
    
    if not supported_files:
        print("⚠️  No supported files found in data/ directory")
        print("   Add some .md, .py, or .txt files to test with")
        return False
    
    print(f"✅ Found {len(supported_files)} files in data/ directory")
    return True

def test_services_running():
    """Test if services are running (if Docker Compose is up)."""
    print("🔍 Testing services...")
    
    # Test PostgreSQL
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname="ragdb",
            user="rag", 
            password="ragpass",
            host="localhost",
            port=5432,
            connect_timeout=5
        )
        conn.close()
        print("✅ PostgreSQL is accessible")
        postgres_ok = True
    except Exception as e:
        print(f"⚠️  PostgreSQL not accessible: {e}")
        postgres_ok = False
    
    # Test Ollama
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is accessible")
            ollama_ok = True
        else:
            print(f"⚠️  Ollama returned status {response.status_code}")
            ollama_ok = False
    except Exception as e:
        print(f"⚠️  Ollama not accessible: {e}")
        ollama_ok = False
    
    return postgres_ok and ollama_ok

def main():
    """Run all tests."""
    print("🧪 RAG System Test Suite")
    print("=" * 30)
    
    tests = [
        test_docker,
        test_python_deps,
        test_data_files,
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
        print()
    
    # Test services only if basic tests pass
    if all_passed:
        print("🚀 Testing running services (optional)...")
        services_ok = test_services_running()
        if not services_ok:
            print("\n💡 To start services, run: docker compose up --build")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 Basic setup looks good!")
        print("\nNext steps:")
        print("1. Start services: docker compose up --build")
        print("2. Wait for services to be ready")
        print("3. Test queries: python rag.py \"test question\"")
    else:
        print("❌ Some issues found. Please fix them before proceeding.")
        print("📚 Check README.md for troubleshooting help.")

if __name__ == "__main__":
    main() 