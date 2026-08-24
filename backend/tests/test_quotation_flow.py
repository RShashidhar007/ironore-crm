#!/usr/bin/env python
"""
Test quotation flow end-to-end
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Test data
USER_ID = "shashi"
PASSWORD = "test123"

def login():
    """Login and get token"""
    print("1. Logging in...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"user_id": USER_ID, "password": PASSWORD}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text}")
        return None
    
    data = response.json()
    token = data.get("access_token")
    print(f"   Token: {token[:20]}...")
    return token

def test_quotation_request(token):
    """Test asking for quotation"""
    print("\n2. Requesting quotation (ask for product list)...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": "Ask for a Quotation"},
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    
    print(f"   Reply: {data['reply'][:100]}...")
    
    if "data" in data and data["data"]:
        products = data["data"].get("products", [])
        print(f"   Products available: {len(products)}")
        if products:
            print(f"   First product: {products[0]}")
            return products[0]
    
    return None

def test_quotation_submission(token, product):
    """Test submitting quotation with product and quantity"""
    if not product:
        print("\nError: No product to submit")
        return
    
    print(f"\n3. Submitting quotation (product: {product['name']}, quantity: 50 MT)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    action = f"submit_quantity_quotation:{product['pid']}:50"
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": f"Generate quotation for {product['name']}, quantity 50 MT", "action": action},
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Reply: {data['reply'][:200]}...")
        
        if "data" in data and data["data"]:
            sd = data["data"]
            print(f"\n   ✓ Quotation Status: {sd.get('status')}")
            if sd.get('quotation_number'):
                print(f"   ✓ Quotation Number: {sd.get('quotation_number')}")
                print(f"   ✓ Product: {sd.get('product_id')}")
                print(f"   ✓ Quantity: {sd.get('quantity_mt')} MT")
                print(f"   ✓ Price/MT: ₹ {sd.get('price_per_mt')}")
                print(f"   ✓ Total: ₹ {sd.get('total_amount')}")
                if sd.get('pdf_path'):
                    print(f"   ✓ PDF: {sd.get('pdf_path')}")
    else:
        print(f"   Error: {response.text}")

def main():
    print("=" * 60)
    print("QUOTATION FLOW TEST")
    print("=" * 60)
    
    token = login()
    if not token:
        print("Failed to login")
        return
    
    product = test_quotation_request(token)
    test_quotation_submission(token, product)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
