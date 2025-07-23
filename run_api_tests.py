#!/usr/bin/env python3
"""
Quick launcher for the standalone API test suite.
This runs only the reference API tests from api_test.py
"""

from api_test import KolosalServerTester

def main():
    print("=" * 60)
    print("KOLOSAL SERVER API TEST SUITE")
    print("Reference Implementation Test Runner")
    print("=" * 60)
    
    # Initialize the tester with default configuration
    tester = KolosalServerTester()
    
    # Run all tests
    success = tester.run_all_tests()
    
    # Print final result
    if success:
        print("\n🎉 All API tests completed successfully!")
        exit(0)
    else:
        print("\n⚠️  Some API tests failed. Check the output above for details.")
        exit(1)

if __name__ == "__main__":
    main()
