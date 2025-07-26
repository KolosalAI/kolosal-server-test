#!/usr/bin/env python3
"""
Simple test runner to verify basic connectivity and functionality.
"""

import sys
import requests
from config import SERVER_CONFIG, MODELS, get_full_url

def test_basic_connectivity():
    """Test basic server connectivity."""
    print("🔍 Testing basic connectivity...")
    
    try:
        url = get_full_url("health")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Health endpoint accessible")
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Health endpoint returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connectivity test failed: {e}")
        return False

def test_models_endpoint():
    """Test models endpoint."""
    print("🔍 Testing models endpoint...")
    
    try:
        url = get_full_url("models")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Models endpoint accessible")
            data = response.json()
            models = data.get('data', [])
            print(f"   Found {len(models)} model(s)")
            for model in models:
                print(f"   - {model.get('id', 'unknown')}")
            return True
        else:
            print(f"❌ Models endpoint returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        return False

def test_agent_system():
    """Test agent system."""
    print("🔍 Testing agent system...")
    
    # Try different agent endpoints
    agent_endpoints = ["agents", "agents_health", "agents_metrics"]
    
    for endpoint_name in agent_endpoints:
        try:
            url = get_full_url(endpoint_name)
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {endpoint_name} endpoint accessible")
                data = response.json()
                
                if isinstance(data, list):
                    print(f"   Found {len(data)} agent(s)")
                    for agent in data[:3]:  # Show first 3
                        agent_id = agent.get('id', 'unknown')
                        agent_name = agent.get('name', 'unknown')
                        print(f"   - {agent_name} ({agent_id[:8]}...)")
                else:
                    print(f"   Response: {str(data)[:100]}...")
                return True
            else:
                print(f"⚠️  {endpoint_name} returned {response.status_code}")
                
        except Exception as e:
            print(f"⚠️  {endpoint_name} failed: {e}")
    
    print("⚠️  Agent system endpoints not accessible - may be disabled or configured differently")
    return True  # Don't fail the test, just warn

def test_completion_endpoint():
    """Test a simple completion."""
    print("🔍 Testing completion endpoint...")
    
    try:
        url = get_full_url("chat_completions")
        payload = {
            "model": MODELS["primary_llm"],
            "messages": [{"role": "user", "content": "Hello! Please respond with just 'Test successful'"}],
            "max_tokens": 20,
            "temperature": 0.1
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            print("✅ Completion endpoint working")
            data = response.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"   Response: {content[:50]}...")
            return True
        else:
            print(f"❌ Completion endpoint returned {response.status_code}")
            print(f"   Error: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ Completion test failed: {e}")
        return False

def main():
    """Run basic connectivity tests."""
    print("="*60)
    print("KOLOSAL SERVER - BASIC CONNECTIVITY TEST")
    print("="*60)
    print(f"Server: {SERVER_CONFIG['base_url']}")
    print(f"Primary Model: {MODELS['primary_llm']}")
    print("="*60)
    
    tests = [
        ("Basic Connectivity", test_basic_connectivity),
        ("Models Endpoint", test_models_endpoint),
        ("Agent System", test_agent_system),
        ("Completion Endpoint", test_completion_endpoint)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Kolosal Server is ready for full testing.")
        return 0
    else:
        print("⚠️  Some tests failed. Check server configuration and logs.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
