"""
Utility to load environment variables from the backend .env file.
Import this at the top of any YouTube script that needs API keys.

Usage:
    from load_env import load_backend_env
    load_backend_env()
    # Now os.environ['YOUTUBE_API_KEY'] is available
"""
import os
from pathlib import Path

def load_backend_env():
    """Load .env from code/backend/ into os.environ (does not override existing vars)."""
    env_path = Path(__file__).resolve().parents[2] / "code" / "backend" / ".env"
    if not env_path.exists():
        print(f"Warning: {env_path} not found, skipping env load")
        return False
    
    with env_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # Don't override if already set in environment
            if key not in os.environ:
                os.environ[key] = value
    return True

if __name__ == "__main__":
    load_backend_env()
    # Quick check (won't print actual values, just confirms presence)
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if api_key and api_key != "your_youtube_data_api_key_here":
        print("✅ YOUTUBE_API_KEY loaded successfully")
    else:
        print("❌ YOUTUBE_API_KEY not configured in code/backend/.env")
