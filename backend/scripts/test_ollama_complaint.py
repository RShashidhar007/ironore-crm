"""
Quick test to verify Ollama is working with complaint generation
"""
import sys
sys.path.insert(0, '.')

from app.ollama_client import generate_reply

# Test the generate_reply function
verified_data = """Complaint Information Retrieved from Database:
- Category: Quality Issue
- Customer Description: Iron ore received has moisture content higher than specification
- PO Number: PO-2024-001
- Dispatch Date: 2024-08-15

Based on this information, please provide a brief summary of the issue and a recommended solution."""

customer_message = """Analyze this complaint and provide:
1. SUMMARY: A brief 2-3 sentence summary of what the customer's issue is
2. SOLUTION: A recommended solution or next steps in 2-3 sentences

Format your response EXACTLY as shown:
SUMMARY: [write summary here]
SOLUTION: [write solution here]"""

print("Testing Ollama connection and complaint generation...")
print("="*60)

response = generate_reply(customer_message, verified_data)

if response:
    print("✓ Ollama responded successfully!")
    print("\nResponse:")
    print("-"*60)
    print(response)
    print("-"*60)
    
    # Try to parse it
    if "SUMMARY:" in response and "SOLUTION:" in response:
        parts = response.split("SOLUTION:")
        summary = parts[0].replace("SUMMARY:", "").strip()
        solution = parts[1].strip()
        
        print("\n✓ Parsing successful!")
        print(f"\nSummary: {summary}")
        print(f"\nSolution: {solution}")
    else:
        print("\n⚠ Response format doesn't match expected pattern")
else:
    print("✗ Ollama did not return a response")
    print("Check if Ollama is running: ollama serve")
