#!/usr/bin/env python
"""
Test "Contact Company via Email" feature
"""
import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = "shashi"
PASSWORD = "test123"

def login():
    """Login and get token"""
    print("1. Logging in...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"user_id": USER_ID, "password": PASSWORD}
    )
    if response.status_code != 200:
        print(f"   Error: {response.text}")
        return None
    
    data = response.json()
    token = data.get("access_token")
    print(f"   ✓ Login successful")
    return token

def test_contact_company(token):
    """Test contact company feature"""
    print("\n2. Testing 'Contact Company via Email' action...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": "Contact Company via Email",
            "action": "Contact Company via Email"
        },
        headers=headers
    )
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n   Reply:")
        print(f"   {data['reply']}")
        
        if "data" in data and data["data"]:
            email = data["data"].get("email")
            if email:
                print(f"\n   ✓ Email retrieved: {email}")
                print(f"   ✓ Mailto link: mailto:{email}")
                return True
            else:
                print(f"   ✗ No email in response")
                return False
        else:
            print(f"   ✗ No data in response")
            return False
    else:
        print(f"   Error: {response.text}")
        return False

def main():
    print("=" * 60)
    print("CONTACT COMPANY VIA EMAIL - TEST")
    print("=" * 60)
    
    token = login()
    if not token:
        print("Failed to login")
        return
    
    success = test_contact_company(token)
    
    print("\n" + "=" * 60)
    if success:
        print("✓ TEST PASSED - Email contact feature working!")
    else:
        print("✗ TEST FAILED")
    print("=" * 60)

if __name__ == "__main__":
    main()
