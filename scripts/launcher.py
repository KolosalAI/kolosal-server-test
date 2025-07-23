#!/usr/bin/env python3
"""
Quick launcher for Kolosal Server tests with endpoint validation.

This script provides a convenient way to run tests with proper configuration validation.
"""

import sys
import argparse
sys.path.append('..')
from utils.endpoint_tester import print_endpoint_report, validate_server_configuration
from config import SERVER_CONFIG, MODELS

def check_prerequisites():
    """Check if all prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    # Validate server configuration
    validation = validate_server_configuration()
    
    if not validation["server_responding"]:
        print("❌ Kolosal Server is not responding")
        print(f"   Expected server at: {SERVER_CONFIG['base_url']}")
        print("   Please ensure the server is running and accessible")
        return False
    
    print("✅ Server is responding")
    
    if not validation["health_endpoint"]:
        print("⚠️  Health endpoint not available - this may be normal")
    else:
        print("✅ Health endpoint available")
    
    if validation["available_models"]:
        print(f"✅ Found {len(validation['available_models'])} model(s)")
        expected_models = [MODELS["primary_llm"], MODELS["alt_llm"], MODELS["embedding_small"]]
        for model in expected_models:
            if model in validation["available_models"]:
                print(f"   ✅ {model}")
            else:
                print(f"   ⚠️  {model} (may not be loaded)")
    else:
        print("⚠️  No models detected - may need to be loaded on demand")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Kolosal Server Test Launcher')
    parser.add_argument('--test-endpoints', action='store_true',
                       help='Test endpoint availability only')
    parser.add_argument('--run-tests', action='store_true',
                       help='Run the full test suite')
    
    args = parser.parse_args()
    
    print("="*60)
    print("KOLOSAL SERVER TEST LAUNCHER")
    print("="*60)
    print(f"Server URL: {SERVER_CONFIG['base_url']}")
    print(f"Models: {MODELS['primary_llm']}, {MODELS['embedding_small']}")
    print("="*60)
    
    if args.test_endpoints:
        print_endpoint_report()
        return
    
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Server may not be ready.")
        print("Cannot proceed without server being ready.")
        sys.exit(1)
    
    if args.run_tests:
        print("\n🚀 Starting test suite...")
        # Import and run main test suite
        import main
    else:
        print("\nUse --run-tests to execute the test suite")
        print("Use --test-endpoints to check endpoint availability")

if __name__ == "__main__":
    main()
