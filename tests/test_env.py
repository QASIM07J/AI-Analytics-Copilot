import sys
import sqlite3
import pandas as pd
import dotenv
import huggingface_hub

def test_environment():
    print(f"Python Executable: {sys.executable}")
    print(f"Python Version:    {sys.version.split()[0]}")
    print(f"Pandas Version:    {pd.__version__}")
    print(f"SQLite Version:    {sqlite3.sqlite_version}")
    # Test loading environment variables
    dotenv.load_dotenv()
    print("Dotenv:            Loaded successfully")
    print(f"HF Hub Version:    {huggingface_hub.__version__}")
    print("\n[SUCCESS] Environment verification completed without errors.")

if __name__ == "__main__":
    test_environment()
