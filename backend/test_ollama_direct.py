"""
Direct test of Ollama API to see if it's working
"""
import httpx

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"

prompt = """You are a professional CRM assistant. Analyze this complaint:

VERIFIED_DATA:
- Category: Quality Issue  
- Description: Iron ore received has moisture content higher than specification
- PO Number: PO-2024-001

Provide:
SUMMARY: [brief summary]
SOLUTION: [recommended solution]"""

print("Testing direct Ollama API call...")
print("="*60)

try:
    with httpx.Client(timeout=120) as client:
        print(f"Calling: {OLLAMA_BASE_URL}/api/generate")
        print(f"Model: {OLLAMA_MODEL}")
        print(f"Prompt length: {len(prompt)} chars\n")
        
        resp = client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2},
            },
        )
        
        print(f"Response status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            text = data.get("response", "").strip()
            
            print("✓ Success!")
            print("\nResponse:")
            print("-"*60)
            print(text)
            print("-"*60)
        else:
            print(f"✗ Error: {resp.text}")
            
except Exception as e:
    print(f"✗ Exception: {type(e).__name__}: {e}")
