#!/usr/bin/env python3
"""
Quick Start Demo for Kolosal Server API

This script demonstrates the complete workflow from the API usage guide:
1. Add knowledge to the system
2. Search the knowledge base
3. Chat with RAG enabled
4. Create and execute workflows

Based on the Kolosal Server API Usage Guide.
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any

def safe_request(func, *args, **kwargs):
    """Safe request wrapper with error handling"""
    try:
        result = func(*args, **kwargs)
        if isinstance(result, dict) and 'error' in result:
            print(f"API Error: {result['error']}")
            return None
        return result
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def chat_with_agent(base_url: str, message: str, session_id: str = "test-session"):
    """Basic chat with agent"""
    url = f"{base_url}/chat"
    payload = {
        "message": message,
        "session_id": session_id
    }
    
    response = requests.post(url, json=payload)
    return response.json()

def rag_chat(base_url: str, message: str, session_id: str = "rag-session", use_context: bool = True):
    """RAG-powered chat (chat with document context)"""
    url = f"{base_url}/chat"
    payload = {
        "message": message,
        "session_id": session_id,
        "use_rag": use_context
    }
    
    response = requests.post(url, json=payload)
    return response.json()

def add_text_content(base_url: str, content: str, title: str, metadata: dict = None):
    """Add text content directly"""
    url = f"{base_url}/documents"
    payload = {
        "content": content,
        "title": title,
        "metadata": metadata or {}
    }
    
    response = requests.post(url, json=payload)
    return response.json()

def upload_document(base_url: str, file_path: str, document_type: str = "text"):
    """Upload documents to knowledge base"""
    url = f"{base_url}/documents/upload"
    
    with open(file_path, 'rb') as file:
        files = {'file': file}
        data = {'type': document_type}
        
        response = requests.post(url, files=files, data=data)
    return response.json()

def search_documents(base_url: str, query: str, limit: int = 5):
    """Search documents using semantic search"""
    url = f"{base_url}/search"
    payload = {
        "query": query,
        "limit": limit
    }
    
    response = requests.post(url, json=payload)
    return response.json()

def advanced_search(base_url: str, query: str, filters: dict = None, sort_by: str = "relevance"):
    """Advanced document search with filters"""
    url = f"{base_url}/search/advanced"
    payload = {
        "query": query,
        "filters": filters or {},
        "sort_by": sort_by
    }
    
    response = requests.post(url, json=payload)
    return response.json()

def create_workflow(base_url: str, name: str, description: str, steps: list):
    """Create a new workflow"""
    url = f"{base_url}/workflows"
    payload = {
        "name": name,
        "description": description,
        "steps": steps
    }
    
    response = requests.post(url, json=payload)
    return response.json()

def execute_workflow(base_url: str, workflow_id: str, inputs: dict = None):
    """Execute a workflow"""
    url = f"{base_url}/workflows/{workflow_id}/execute"
    payload = {"inputs": inputs or {}}
    
    response = requests.post(url, json=payload)
    return response.json()

def get_chat_history(base_url: str, session_id: str):
    """Get chat history"""
    url = f"{base_url}/sessions/{session_id}/history"
    response = requests.get(url)
    return response.json()

def clear_session(base_url: str, session_id: str):
    """Clear session"""
    url = f"{base_url}/sessions/{session_id}/clear"
    response = requests.delete(url)
    return response.json()

def complete_rag_workflow(base_url: str):
    """Complete example workflow from the API guide"""
    print("🚀 Starting Complete RAG Workflow Demo")
    print("=" * 50)
    
    results = {}
    
    # 1. Upload knowledge
    print("📚 Step 1: Adding knowledge content...")
    doc = safe_request(add_text_content,
        base_url,
        content="Our premium software package costs $299/month and includes 24/7 support.",
        title="Pricing Information"
    )
    
    if doc:
        print(f"✅ Document added: {doc.get('id', 'Unknown ID')}")
        results['document'] = doc
    else:
        print("❌ Failed to add document")
        results['document'] = None
    
    # 2. Search for relevant info
    print("\n🔍 Step 2: Searching for pricing information...")
    search_results = safe_request(search_documents, base_url, "software pricing")
    
    if search_results:
        results_count = len(search_results.get('results', []))
        print(f"✅ Found {results_count} search results")
        results['search'] = search_results
    else:
        print("❌ Search failed")
        results['search'] = None
    
    # 3. Chat with RAG context
    print("\n💬 Step 3: Testing RAG-enabled chat...")
    response = safe_request(rag_chat, base_url, "How much does the premium package cost?")
    
    if response:
        chat_response = response.get('response', '')
        context_used = response.get('context_used', False)
        print(f"✅ Chat response received (length: {len(chat_response)}, context used: {context_used})")
        print(f"Response preview: {chat_response[:100]}...")
        results['chat'] = response
    else:
        print("❌ RAG chat failed")
        results['chat'] = None
    
    # 4. Create workflow for customer inquiry
    print("\n⚙️ Step 4: Creating customer inquiry workflow...")
    workflow = safe_request(create_workflow,
        base_url,
        name="Customer Inquiry Handler",
        description="Handle customer pricing questions",
        steps=[
            {"name": "search_docs", "type": "retrieval"},
            {"name": "generate_response", "type": "generation"}
        ]
    )
    
    if workflow:
        workflow_id = workflow.get('id') or workflow.get('workflow_id')
        print(f"✅ Workflow created: {workflow_id}")
        results['workflow'] = workflow
        
        # 5. Execute workflow
        print("\n🚀 Step 5: Executing workflow...")
        execution_result = safe_request(execute_workflow, 
            base_url,
            workflow_id, 
            {"customer_question": "What are your pricing options?"}
        )
        
        if execution_result:
            execution_id = execution_result.get('execution_id') or execution_result.get('id')
            print(f"✅ Workflow executed: {execution_id}")
            results['execution'] = execution_result
        else:
            print("❌ Workflow execution failed")
            results['execution'] = None
    else:
        print("❌ Workflow creation failed")
        results['workflow'] = None
    
    return results

def quick_start_demo(base_url: str = "http://127.0.0.1:8080"):
    """Complete example combining all features"""
    print("🎯 Quick Start Demo - Testing All Features")
    print("=" * 50)
    
    # 1. Add some knowledge
    print("📚 Adding knowledge to the system...")
    knowledge = {
        "content": "Our AI service offers three tiers: Basic ($50/month), Pro ($150/month), and Enterprise ($500/month).",
        "title": "Service Pricing",
        "metadata": {"category": "pricing"}
    }
    doc_response = requests.post(f"{base_url}/documents", json=knowledge)
    if doc_response.status_code == 200:
        print("✅ Knowledge added successfully")
    else:
        print(f"❌ Failed to add knowledge: {doc_response.status_code}")
    
    # 2. Search the knowledge
    print("\n🔍 Searching the knowledge base...")
    search_payload = {"query": "pricing tiers", "limit": 3}
    search_result = requests.post(f"{base_url}/search", json=search_payload)
    
    if search_result.status_code == 200:
        search_data = search_result.json()
        results_count = len(search_data.get('results', []))
        print(f"✅ Search successful: Found {results_count} results")
    else:
        print(f"❌ Search failed: {search_result.status_code}")
    
    # 3. Chat with RAG
    print("\n💬 Testing RAG-enabled chat...")
    chat_payload = {
        "message": "What are your pricing options?",
        "session_id": "demo-session",
        "use_rag": True
    }
    chat_result = requests.post(f"{base_url}/chat", json=chat_payload)
    
    if chat_result.status_code == 200:
        chat_data = chat_result.json()
        response_text = chat_data.get('response', '')
        print(f"✅ RAG chat successful")
        print(f"Response preview: {response_text[:100]}...")
    else:
        print(f"❌ RAG chat failed: {chat_result.status_code}")
    
    # 4. Create and execute workflow
    print("\n⚙️ Testing workflow functionality...")
    workflow_payload = {
        "name": "Pricing Inquiry",
        "description": "Handle pricing questions",
        "steps": [
            {"name": "retrieve_pricing", "type": "retrieval"},
            {"name": "format_response", "type": "generation"}
        ]
    }
    workflow_result = requests.post(f"{base_url}/workflows", json=workflow_payload)
    
    if workflow_result.status_code == 200:
        workflow_data = workflow_result.json()
        workflow_id = workflow_data.get('id') or workflow_data.get('workflow_id')
        print(f"✅ Workflow created: {workflow_id}")
        
        # Execute the workflow
        execution_payload = {"inputs": {"query": "enterprise pricing"}}
        execution_result = requests.post(f"{base_url}/workflows/{workflow_id}/execute", json=execution_payload)
        
        if execution_result.status_code == 200:
            print("✅ Workflow executed successfully")
        else:
            print(f"❌ Workflow execution failed: {execution_result.status_code}")
    else:
        print(f"❌ Workflow creation failed: {workflow_result.status_code}")
    
    print("\n🏁 Quick start demo completed!")

def test_basic_functionality(base_url: str = "http://127.0.0.1:8080"):
    """Test basic functionality step by step"""
    print("🧪 Testing Basic Kolosal Server Functionality")
    print("=" * 50)
    
    test_results = {
        'basic_chat': False,
        'document_add': False,
        'document_search': False,
        'rag_chat': False,
        'workflow_create': False,
        'workflow_execute': False
    }
    
    # Test 1: Basic Chat
    print("\n1️⃣ Testing basic chat...")
    try:
        result = chat_with_agent(base_url, "Hello! Can you help me?")
        if result and result.get('response'):
            print("✅ Basic chat: PASS")
            test_results['basic_chat'] = True
        else:
            print("❌ Basic chat: FAIL - No response")
    except Exception as e:
        print(f"❌ Basic chat: FAIL - {e}")
    
    # Test 2: Document Addition
    print("\n2️⃣ Testing document addition...")
    try:
        result = add_text_content(
            base_url,
            content="Test content about AI and machine learning capabilities.",
            title="AI Information",
            metadata={"category": "technology"}
        )
        if result and (result.get('id') or result.get('document_id')):
            print("✅ Document addition: PASS")
            test_results['document_add'] = True
        else:
            print("❌ Document addition: FAIL - No document ID")
    except Exception as e:
        print(f"❌ Document addition: FAIL - {e}")
    
    # Test 3: Document Search
    print("\n3️⃣ Testing document search...")
    try:
        result = search_documents(base_url, "AI machine learning")
        if result and isinstance(result.get('results'), list):
            print(f"✅ Document search: PASS - Found {len(result['results'])} results")
            test_results['document_search'] = True
        else:
            print("❌ Document search: FAIL - No results")
    except Exception as e:
        print(f"❌ Document search: FAIL - {e}")
    
    # Test 4: RAG Chat
    print("\n4️⃣ Testing RAG-enabled chat...")
    try:
        result = rag_chat(base_url, "What do you know about AI?")
        if result and result.get('response'):
            print("✅ RAG chat: PASS")
            test_results['rag_chat'] = True
        else:
            print("❌ RAG chat: FAIL - No response")
    except Exception as e:
        print(f"❌ RAG chat: FAIL - {e}")
    
    # Test 5: Workflow Creation
    print("\n5️⃣ Testing workflow creation...")
    try:
        result = create_workflow(
            base_url,
            name="Test Analysis Workflow",
            description="Simple test workflow",
            steps=[{"name": "analyze", "type": "analysis"}]
        )
        workflow_id = None
        if result and (result.get('id') or result.get('workflow_id')):
            workflow_id = result.get('id') or result.get('workflow_id')
            print("✅ Workflow creation: PASS")
            test_results['workflow_create'] = True
            
            # Test 6: Workflow Execution
            print("\n6️⃣ Testing workflow execution...")
            try:
                exec_result = execute_workflow(workflow_id, {"test": "data"})
                if exec_result and (exec_result.get('execution_id') or exec_result.get('id')):
                    print("✅ Workflow execution: PASS")
                    test_results['workflow_execute'] = True
                else:
                    print("❌ Workflow execution: FAIL - No execution ID")
            except Exception as e:
                print(f"❌ Workflow execution: FAIL - {e}")
        else:
            print("❌ Workflow creation: FAIL - No workflow ID")
    except Exception as e:
        print(f"❌ Workflow creation: FAIL - {e}")
    
    # Summary
    passed = sum(test_results.values())
    total = len(test_results)
    success_rate = (passed / total) * 100
    
    print(f"\n📊 Test Summary:")
    print(f"✅ Passed: {passed}/{total}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 70:
        print("🎉 Overall: PASS - Server is functioning well!")
    elif success_rate >= 50:
        print("⚠️ Overall: PARTIAL - Some functionality working")
    else:
        print("❌ Overall: FAIL - Significant issues detected")
    
    return test_results

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Kolosal Server Quick Start Demo')
    parser.add_argument('--server-url', default='http://127.0.0.1:8080',
                        help='Base URL of the Kolosal Server')
    parser.add_argument('--mode', choices=['demo', 'test', 'workflow'], default='demo',
                        help='Demo mode: demo (quick), test (comprehensive), workflow (RAG workflow)')
    
    args = parser.parse_args()
    
    print(f"🌟 Kolosal Server Quick Start")
    print(f"📡 Server: {args.server_url}")
    print(f"🎯 Mode: {args.mode}")
    
    try:
        if args.mode == 'demo':
            quick_start_demo(args.server_url)
        elif args.mode == 'test':
            test_basic_functionality(args.server_url)
        elif args.mode == 'workflow':
            complete_rag_workflow(args.server_url)
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")

if __name__ == "__main__":
    main()
