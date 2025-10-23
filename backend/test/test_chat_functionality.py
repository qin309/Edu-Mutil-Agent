#!/usr/bin/env python3
"""
Test script to verify simplified chat functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import httpx

async def test_simplified_chat():
    """Test if the simplified chat API works correctly"""
    
    print("Testing simplified chat functionality...")
    
    # Test data
    test_messages = [
        ("你好", "Chinese greeting"),
        ("Hello, how are you?", "English greeting"), 
        ("What is machine learning?", "Technical question"),
        ("请解释一下深度学习的原理", "Chinese technical question"),
        ("How does transformer architecture work?", "Complex technical question")
    ]
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            for message, description in test_messages:
                print(f"\n📝 Testing {description}: '{message}'")
                
                # Test the simplified chat endpoint
                response = await client.post(
                    f"{base_url}/api/chat/message",
                    json={
                        "message": message,
                        "student_id": "test_user",
                        "model": "Pro/moonshotai/Kimi-K2-Instruct-0905"
                    },
                    headers={
                        "Content-Type": "application/json"
                    }
                )
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ SUCCESS!")
                    print(f"Response preview: {result.get('response', '')[:100]}...")
                    print(f"Sources: {result.get('sources', [])}")
                    
                    # Check response quality
                    response_text = result.get('response', '')
                    if "technical difficulties" in response_text.lower():
                        print("⚠️  WARNING: Getting error response")
                    elif "I apologize" in response_text:
                        print("⚠️  WARNING: Getting apologetic response")
                    elif len(response_text) < 20:
                        print("⚠️  WARNING: Response seems too short")
                    else:
                        print("✅ GOOD: Getting proper AI response")
                        
                else:
                    print(f"❌ ERROR: {response.status_code}")
                    print(f"Response: {response.text}")
                
                print("-" * 60)
                
    except httpx.ConnectError:
        print("❌ ERROR: Cannot connect to backend server")
        print("Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Simplified Chat Functionality")
    print("=" * 60)
    asyncio.run(test_simplified_chat())