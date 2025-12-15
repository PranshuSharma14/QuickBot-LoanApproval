"""
Test script to verify all edge case handling in the NBFC Loan Assistant
"""

import requests
import json

API_URL = "http://localhost:8000/api/chat"

def test_edge_case(test_name, message, expected_keyword=None):
    """Test a specific edge case"""
    print(f"\n{'='*60}")
    print(f"🧪 TEST: {test_name}")
    print(f"{'='*60}")
    print(f"Input: {message}")
    
    try:
        response = requests.post(API_URL, json={"message": message})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: SUCCESS")
            print(f"Response: {data['message'][:200]}...")
            
            if expected_keyword:
                if expected_keyword.lower() in data['message'].lower():
                    print(f"✅ Contains expected keyword: '{expected_keyword}'")
                else:
                    print(f"❌ Missing expected keyword: '{expected_keyword}'")
        else:
            print(f"❌ Status: FAILED - {response.status_code}")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

# Run edge case tests
print("\n" + "="*60)
print("🚀 NBFC LOAN ASSISTANT - EDGE CASE TESTING")
print("="*60)

# Test 1: Empty message
test_edge_case(
    "Empty Message",
    "",
    "didn't receive"
)

# Test 2: Very long message (spam)
test_edge_case(
    "Very Long Message (>2000 chars)",
    "a" * 2500,
    "too long"
)

# Test 3: Exit command
test_edge_case(
    "Exit Command",
    "quit",
    "Thank you"
)

# Test 4: Help request
test_edge_case(
    "Help Request",
    "help",
    "guide you"
)

# Test 5: Abusive content
test_edge_case(
    "Abusive Content",
    "this is shit",
    "professional"
)

# Test 6: Email instead of phone (in verification stage)
print("\n" + "="*60)
print("🔄 Multi-stage edge case test")
print("="*60)

# Start conversation
session_id = None
response = requests.post(API_URL, json={"message": "Hi"})
if response.status_code == 200:
    data = response.json()
    session_id = data['session_id']
    print(f"✅ Session started: {session_id}")
    
    # Progress to sales
    response = requests.post(API_URL, json={"message": "I need 50000 rupees", "session_id": session_id})
    print(f"✅ Loan amount provided")
    
    # Provide tenure
    response = requests.post(API_URL, json={"message": "12 months", "session_id": session_id})
    print(f"✅ Tenure provided")
    
    # Provide purpose
    response = requests.post(API_URL, json={"message": "personal expenses", "session_id": session_id})
    print(f"✅ Purpose provided")
    
    # Now in verification stage - provide email instead of phone
    print("\n🧪 Testing email instead of phone in verification stage...")
    response = requests.post(API_URL, json={"message": "my email is test@example.com", "session_id": session_id})
    if response.status_code == 200:
        data = response.json()
        if "mobile number" in data['message'].lower():
            print(f"✅ Correctly asked for mobile number instead")
            print(f"Response: {data['message'][:150]}...")
        else:
            print(f"❌ Did not handle email edge case properly")
    
    # Test Aadhaar/PAN confusion
    print("\n🧪 Testing document number confusion in verification stage...")
    response = requests.post(API_URL, json={"message": "my aadhaar is 1234 5678 9012", "session_id": session_id})
    if response.status_code == 200:
        data = response.json()
        if "mobile number" in data['message'].lower():
            print(f"✅ Correctly redirected from Aadhaar to mobile number")
            print(f"Response: {data['message'][:150]}...")
        else:
            print(f"❌ Did not handle Aadhaar confusion properly")

# Test 7: Clarification questions in sales stage
print("\n🧪 Testing clarification questions...")
response = requests.post(API_URL, json={"message": "what is the minimum loan amount"})
if response.status_code == 200:
    data = response.json()
    if "10,000" in data['message'] or "10000" in data['message']:
        print(f"✅ Correctly answered minimum loan amount question")
        print(f"Response: {data['message'][:200]}...")
    else:
        print(f"❌ Did not answer clarification question properly")

print("\n" + "="*60)
print("🏁 EDGE CASE TESTING COMPLETED")
print("="*60)
print("\n💡 Check the results above to verify all edge cases are handled correctly.")
print("✅ = Passed | ❌ = Failed")
