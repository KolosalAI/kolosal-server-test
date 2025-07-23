"""
Endpoint testing utilities for Kolosal Server Test Suite.

This module provides utilities to test and validate server endpoints
based on the actual Kolosal Server configuration.
"""

import requests
from typing import Dict, List, Optional, Tuple
from config import SERVER_CONFIG, ENDPOINTS, get_full_url

def test_endpoint_availability() -> Dict[str, bool]:
    """Test availability of all known endpoints."""
    results = {}
    
    for endpoint_name, endpoint_path in ENDPOINTS.items():
        try:
            url = get_full_url(endpoint_name)
            response = requests.get(url, timeout=5)
            # Consider 200, 404, 405 as "server responding" 
            # 404/405 means endpoint exists but may not support GET
            results[endpoint_name] = response.status_code in [200, 404, 405]
        except Exception:
            results[endpoint_name] = False
    
    return results

def get_available_endpoints() -> List[str]:
    """Get list of available endpoint names."""
    availability = test_endpoint_availability()
    return [name for name, available in availability.items() if available]

def test_specific_endpoints(endpoint_names: List[str]) -> Dict[str, Tuple[bool, int, str]]:
    """Test specific endpoints and return detailed results.
    
    Returns:
        Dict mapping endpoint name to (success, status_code, response_text)
    """
    results = {}
    
    for endpoint_name in endpoint_names:
        if endpoint_name not in ENDPOINTS:
            results[endpoint_name] = (False, 0, f"Unknown endpoint: {endpoint_name}")
            continue
            
        try:
            url = get_full_url(endpoint_name)
            response = requests.get(url, timeout=10)
            success = response.status_code == 200
            results[endpoint_name] = (success, response.status_code, response.text[:200])
        except Exception as e:
            results[endpoint_name] = (False, 0, str(e))
    
    return results

def get_server_models() -> Optional[List[Dict]]:
    """Get available models from the server."""
    try:
        url = get_full_url("models")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", [])
    except Exception:
        pass
    return None

def get_server_health() -> Optional[Dict]:
    """Get server health information."""
    try:
        url = get_full_url("health")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

def get_agent_system_health() -> Optional[Dict]:
    """Get agent system health information."""
    try:
        url = get_full_url("agents_health")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

def validate_server_configuration() -> Dict[str, any]:
    """Validate that the server matches expected configuration."""
    validation_results = {
        "server_responding": False,
        "health_endpoint": False,
        "models_endpoint": False,
        "agent_system": False,
        "available_models": [],
        "agent_count": 0,
        "errors": []
    }
    
    # Test basic connectivity
    try:
        response = requests.get(SERVER_CONFIG["base_url"], timeout=5)
        validation_results["server_responding"] = response.status_code in [200, 404, 405]
    except Exception as e:
        validation_results["errors"].append(f"Server connection failed: {e}")
    
    # Test health endpoint
    health_data = get_server_health()
    if health_data:
        validation_results["health_endpoint"] = True
        validation_results["health_status"] = health_data.get("status")
    
    # Test models endpoint
    models_data = get_server_models()
    if models_data:
        validation_results["models_endpoint"] = True
        validation_results["available_models"] = [model.get("id") for model in models_data]
    
    # Test agent system
    agent_health = get_agent_system_health()
    if agent_health:
        validation_results["agent_system"] = True
        validation_results["agent_count"] = agent_health.get("agent_count", 0)
    
    return validation_results

def print_endpoint_report():
    """Print a comprehensive endpoint availability report."""
    print("\n" + "="*60)
    print("KOLOSAL SERVER ENDPOINT REPORT")
    print("="*60)
    
    # Basic server validation
    validation = validate_server_configuration()
    
    print(f"Server Status: {'✅ Online' if validation['server_responding'] else '❌ Offline'}")
    print(f"Health Endpoint: {'✅ Available' if validation['health_endpoint'] else '❌ Unavailable'}")
    print(f"Models Endpoint: {'✅ Available' if validation['models_endpoint'] else '❌ Unavailable'}")
    print(f"Agent System: {'✅ Available' if validation['agent_system'] else '❌ Unavailable'}")
    
    if validation['available_models']:
        print(f"\nAvailable Models ({len(validation['available_models'])}):")
        for model in validation['available_models']:
            print(f"  - {model}")
    
    if validation['agent_count'] > 0:
        print(f"\nAgent System: {validation['agent_count']} agents detected")
    
    # Test all endpoints
    print("\nEndpoint Availability:")
    availability = test_endpoint_availability()
    
    available_count = sum(1 for available in availability.values() if available)
    total_count = len(availability)
    
    print(f"Available: {available_count}/{total_count} endpoints")
    
    for endpoint_name, available in availability.items():
        status = "✅" if available else "❌"
        url = get_full_url(endpoint_name)
        print(f"  {status} {endpoint_name}: {url}")
    
    if validation['errors']:
        print("\nErrors:")
        for error in validation['errors']:
            print(f"  ❌ {error}")
    
    print("="*60)

if __name__ == "__main__":
    print_endpoint_report()
