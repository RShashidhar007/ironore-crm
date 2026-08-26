#!/usr/bin/env python
"""
Test complaint solution generation flow end-to-end

This test verifies:
1. Create a complaint with initial description
2. Add RCA (Root Cause Analysis)
3. Add CAPA (Corrective and Preventive Action)
4. Add Marketing Review
5. Add Plant Head Review (should trigger auto-generation of solution)
6. Verify solution is present in the API response
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# Test data
USER_ID = "shashi"
PASSWORD = "test123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

def print_section(title):
    print(f"\n{Colors.BLUE}{'='*70}")
    print(f"{title}")
    print(f"{'='*70}{Colors.ENDC}")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.YELLOW}ℹ {msg}{Colors.ENDC}")

def login():
    """Login and get token"""
    print_info("Logging in...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"user_id": USER_ID, "password": PASSWORD}
    )
    
    if response.status_code != 200:
        print_error(f"Login failed: {response.text}")
        return None
    
    data = response.json()
    token = data.get("access_token")
    print_success(f"Login successful. Token: {token[:20]}...")
    return token

def create_complaint(token):
    """Step 1: Create a new complaint"""
    print_info("Creating complaint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    payload = {
        "category_type": "Quality Issue",
        "description": "Iron ore shipment received with lower than expected iron content. Sample batch shows 62% Fe instead of 65% Fe.",
        "po_number": "PO-2026-08-001",
        "dispatch_date": today
    }
    
    response = requests.post(
        f"{BASE_URL}/api/complaints",
        json=payload,
        headers=headers
    )
    
    if response.status_code != 200:
        print_error(f"Failed to create complaint: {response.text}")
        return None
    
    data = response.json()
    complaint_id = data.get("ComplaintID")
    print_success(f"Complaint created: {complaint_id}")
    print_info(f"Status: {data.get('Status')}")
    print_info(f"Solution: {data.get('Solution')}")
    
    return complaint_id, data

def add_rca(token, complaint_id):
    """Step 2: Add Root Cause Analysis"""
    print_info("Adding Root Cause Analysis...")
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "complaint_id": complaint_id,
        "root_cause_analysis": "Analysis shows that raw ore batch was collected from a different mining zone with naturally lower iron content. Quality control at mining site did not catch this variation before shipment.",
        "corrective_preventive_action": ""
    }
    
    response = requests.put(
        f"{BASE_URL}/api/complaints/{complaint_id}/analysis",
        json=payload,
        headers=headers
    )
    
    if response.status_code != 200:
        print_error(f"Failed to add RCA: {response.text}")
        return None
    
    data = response.json()
    print_success("RCA added")
    print_info(f"Solution present: {'Yes' if data.get('Solution') else 'No'}")
    
    return data

def add_capa(token, complaint_id):
    """Step 3: Add Corrective and Preventive Action"""
    print_info("Adding Corrective and Preventive Action...")
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "complaint_id": complaint_id,
        "root_cause_analysis": "Analysis shows that raw ore batch was collected from a different mining zone with naturally lower iron content. Quality control at mining site did not catch this variation before shipment.",
        "corrective_preventive_action": "1. CORRECTIVE: Offer customer credit note for the difference in iron content. 2. PREVENTIVE: Implement additional quality checks at mining site. Deploy spectroscopy equipment to verify iron content before shipment. Establish weekly audits with mining teams."
    }
    
    response = requests.put(
        f"{BASE_URL}/api/complaints/{complaint_id}/analysis",
        json=payload,
        headers=headers
    )
    
    if response.status_code != 200:
        print_error(f"Failed to add CAPA: {response.text}")
        return None
    
    data = response.json()
    print_success("CAPA added")
    print_info(f"Solution present: {'Yes' if data.get('Solution') else 'No'}")
    
    return data

def add_marketing_review(token, complaint_id):
    """Step 4: Add Marketing Head Review"""
    print_info("Adding Marketing Head Review...")
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "complaint_id": complaint_id,
        "review_type": "marketing",
        "approval_status": "approved",
        "review_comments": "Customer relationship stable. Recommend goodwill gesture to maintain business."
    }
    
    response = requests.post(
        f"{BASE_URL}/api/complaints/review",
        json=payload,
        headers=headers
    )
    
    if response.status_code != 200:
        print_error(f"Failed to add marketing review: {response.text}")
        return None
    
    data = response.json()
    print_success("Marketing Review added")
    print_info(f"Marketing Review: {data.get('MarketingReview')}")
    print_info(f"Solution present: {'Yes' if data.get('Solution') else 'No'}")
    
    return data

def add_plant_head_review(token, complaint_id):
    """Step 5: Add Plant Head Review (SHOULD TRIGGER SOLUTION GENERATION)"""
    print_info("Adding Plant Head Review (THIS SHOULD TRIGGER SOLUTION GENERATION)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "complaint_id": complaint_id,
        "review_type": "plant_head",
        "approval_status": "approved",
        "review_comments": "Quality issue acknowledged. Proposed solution acceptable. Implementation can proceed."
    }
    
    response = requests.post(
        f"{BASE_URL}/api/complaints/review",
        json=payload,
        headers=headers
    )
    
    if response.status_code != 200:
        print_error(f"Failed to add plant head review: {response.text}")
        return None
    
    data = response.json()
    print_success("Plant Head Review added")
    print_info(f"Plant Head Review: {data.get('PlantHeadReview')}")
    
    return data

def verify_solution_generated(token, complaint_id, response_data, wait_time=40):
    """
    Step 6: Verify solution was auto-generated
    
    Note: Solution generation is now asynchronous via background scheduler.
    The scheduler checks every 30 seconds for complaints ready for generation.
    We'll wait up to wait_time seconds and poll the API.
    """
    import time
    
    print_info(f"Verifying solution generation (waiting up to {wait_time} seconds)...")
    print_info("Note: Solution generation is handled asynchronously by the background scheduler")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check from the response data first
    solution = response_data.get("Solution")
    status = response_data.get("Status")
    
    print_info(f"Initial Status: {status}")
    
    if solution:
        print_success("SOLUTION GENERATED!")
        print(f"\n{Colors.BLUE}Generated Solution:{Colors.ENDC}")
        print(f"{solution}\n")
        return True
    
    # Poll the API until solution appears or timeout
    print_info("Solution not in initial response. Polling API for background generation...")
    start_time = time.time()
    poll_interval = 5  # Check every 5 seconds
    
    while time.time() - start_time < wait_time:
        time.sleep(poll_interval)
        elapsed = int(time.time() - start_time)
        
        response = requests.get(
            f"{BASE_URL}/api/complaints/{complaint_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            solution = data.get("Solution")
            status = data.get("Status")
            
            print_info(f"[{elapsed}s] Status: {status}, Solution present: {'Yes' if solution else 'No'}")
            
            if solution:
                print_success("SOLUTION GENERATED!")
                print(f"\n{Colors.BLUE}Generated Solution:{Colors.ENDC}")
                print(f"{solution}\n")
                return True
    
    print_error(f"Solution not generated after {wait_time} seconds")
    print_error("Solution generation may have failed in the background scheduler")
    return False

def print_complaint_details(data):
    """Pretty print complaint details"""
    print(f"\n{Colors.BLUE}Complaint Details:{Colors.ENDC}")
    print(f"  ID: {data.get('ComplaintID')}")
    print(f"  Category: {data.get('CategoryType')}")
    print(f"  Description: {data.get('ComplaintDescription')[:60]}...")
    print(f"  PO Number: {data.get('PONumber')}")
    print(f"  Status: {data.get('Status')}")
    print(f"  Created: {data.get('CreatedDate')}")
    print(f"\n{Colors.BLUE}Review Status:{Colors.ENDC}")
    print(f"  RCA: {'✓' if data.get('RootCauseAnalysis') else '✗'}")
    print(f"  CAPA: {'✓' if data.get('CorrectivePreventiveAction') else '✗'}")
    print(f"  Marketing Review: {data.get('MarketingReview') or '✗'}")
    print(f"  Plant Head Review: {data.get('PlantHeadReview') or '✗'}")
    print(f"  Solution: {'✓' if data.get('Solution') else '✗'}")

def main():
    print_section("COMPLAINT SOLUTION GENERATION FLOW TEST")
    
    # Step 1: Login
    token = login()
    if not token:
        print_error("Cannot proceed without token")
        return
    
    # Step 2: Create complaint
    complaint_data = create_complaint(token)
    if not complaint_data:
        print_error("Cannot proceed without complaint")
        return
    
    complaint_id, data = complaint_data
    print_complaint_details(data)
    
    # Step 3: Add RCA
    data = add_rca(token, complaint_id)
    if not data:
        return
    
    # Step 4: Add CAPA
    data = add_capa(token, complaint_id)
    if not data:
        return
    
    # Step 5: Add Marketing Review
    data = add_marketing_review(token, complaint_id)
    if not data:
        return
    
    # Step 6: Add Plant Head Review (SHOULD TRIGGER SOLUTION)
    data = add_plant_head_review(token, complaint_id)
    if not data:
        return
    
    # Step 7: Verify solution
    print_section("SOLUTION GENERATION VERIFICATION")
    success = verify_solution_generated(token, complaint_id, data)
    
    if success:
        print_section("TEST PASSED ✓")
    else:
        print_section("TEST FAILED ✗")
        print_info("Solution was not generated. This may indicate an issue with:")
        print_info("  1. Solution generation logic in regenerate_solution_if_conditions_met()")
        print_info("  2. Ollama connection or model")
        print_info("  3. Database update not persisting")

if __name__ == "__main__":
    main()
