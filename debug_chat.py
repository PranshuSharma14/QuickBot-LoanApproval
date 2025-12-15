"""
Test script to debug the chat response issue
"""
import asyncio
import requests
import json

async def test_chat_response():
    """Test the actual backend response to see what's being returned"""
    
    print("🔍 Testing Chat API Response...")
    
    # Test the exact scenario that's getting stuck
    test_messages = [
        {"message": "Hi, I need a personal loan", "session_id": "debug_test_001"},
        {"message": "9876543210", "session_id": "debug_test_001"},  # Rajesh Kumar
        {"message": "I need 5 lakhs for home renovation", "session_id": "debug_test_001"}
    ]
    
    for i, msg in enumerate(test_messages):
        print(f"\n📤 Sending message {i+1}: {msg['message']}")
        
        try:
            response = requests.post('http://127.0.0.1:8000/api/chat', json=msg, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response received:")
                print(f"   Stage: {data.get('stage')}")
                print(f"   Message length: {len(data.get('message', ''))}")
                print(f"   Has options: {'options' in data and data['options'] is not None}")
                print(f"   Options: {data.get('options')}")
                print(f"   Requires input: {data.get('requires_input')}")
                print(f"   Final: {data.get('final')}")
                
                # Show first 200 chars of message
                message = data.get('message', '')
                print(f"   Message preview: {message[:200]}...")
                
                if data.get('stage') == 'decision':
                    print(f"\n🎯 DECISION STAGE RESPONSE:")
                    print(f"   Full message: {message}")
                    print(f"   Options available: {data.get('options')}")
                    break
                    
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_chat_response())