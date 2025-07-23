#!/usr/bin/env python3
"""
Basic connectivity test for Kolosal Server.

Quick test to verify server is running and accessible.
"""

import requests
import sys
from config import SERVER_CONFIG

def test_basic_connectivity():
    """Test basic server connectivity."""
    base_url = SERVER_CONFIG["base_url"]
    
    print(f"🔍 Testing connectivity to {base_url}")
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is responding - Health check passed")
            return True
        else:
            print(f"❌ Server responded with status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to server at {base_url}")
        print("   Make sure Kolosal Server is running")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Connection timeout to {base_url}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_basic_connectivity()
    sys.exit(0 if success else 1)
