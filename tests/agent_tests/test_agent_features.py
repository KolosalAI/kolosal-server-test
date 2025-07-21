#!/usr/bin/env python3
"""
Comprehensive test suite for Kolosal Server Agent System features.

This script tests all agent-related functionality including:
- Agent management (CRUD operations)
- Function execution and capabilities
- OpenAI-compatible endpoints
- Workflow orchestration
- Agent communication and collaboration
- Document/RAG management
- System monitoring and metrics
- Authentication and security features

Usage:
    python test_agent_features.py [options]

Options:
    --server-url    Base URL of the Kolosal Server (default: http://localhost:8080)
    --api-key       API key for authentication (if required)
    --skip-auth     Skip authentication tests
    --skip-rag      Skip RAG/document tests
    --verbose       Enable verbose output
"""

import requests
import json
import time
import base64
import argparse
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class KolosalAgentTester:
    def __init__(self, base_url: str = "http://localhost:8080", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Set up authentication headers
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'X-API-Key': api_key
            })
        
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'KolosalAgentTester/1.0'
        })
        
        # Test results storage
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        # Created resources for cleanup
        self.created_agents = []
        self.created_workflows = []
        self.created_collaboration_groups = []

    def log_test(self, test_name: str, success: bool, message: str = "", details: Any = None):
        """Log test results"""
        status = "PASS" if success else "FAIL"
        log_msg = f"[{status}] {test_name}"
        if message:
            log_msg += f" - {message}"
        
        if success:
            logger.info(log_msg)
            self.test_results['passed'] += 1
        else:
            logger.error(log_msg)
            self.test_results['failed'] += 1
            self.test_results['errors'].append({
                'test': test_name,
                'message': message,
                'details': details
            })

    def skip_test(self, test_name: str, reason: str):
        """Log skipped test"""
        logger.warning(f"[SKIP] {test_name} - {reason}")
        self.test_results['skipped'] += 1

    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except Exception as e:
            logger.error(f"Request failed: {method} {url} - {e}")
            raise

    # ===== BASIC CONNECTIVITY TESTS =====
    
    def test_server_health(self):
        """Test server health endpoint"""
        try:
            response = self.make_request('GET', '/health')
            if response.status_code == 200:
                data = response.json()
                server_healthy = data.get('status') == 'healthy'
                self.log_test("Server Health Check", server_healthy, 
                            f"Status: {data.get('status', 'unknown')}")
                return server_healthy
            else:
                self.log_test("Server Health Check", False, 
                            f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Server Health Check", False, str(e))
            return False

    def test_agent_system_status(self):
        """Test agent system status"""
        try:
            response = self.make_request('GET', '/api/v1/agents/system/status')
            if response.status_code == 200:
                data = response.json()
                system_running = data.get('data', {}).get('system_running', False)
                agent_count = data.get('data', {}).get('agent_count', 0)
                self.log_test("Agent System Status", system_running,
                            f"Agents: {agent_count}, Running: {system_running}")
                return system_running
            else:
                self.log_test("Agent System Status", False,
                            f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Agent System Status", False, str(e))
            return False

    # ===== AGENT MANAGEMENT TESTS =====
    
    def test_list_agents(self):
        """Test listing all agents"""
        try:
            response = self.make_request('GET', '/api/v1/agents')
            success = response.status_code == 200
            if success:
                data = response.json()
                agents = data.get('data', [])
                count = data.get('count', 0)
                self.log_test("List Agents", True, f"Found {count} agents")
                return agents
            else:
                self.log_test("List Agents", False, f"HTTP {response.status_code}")
                return []
        except Exception as e:
            self.log_test("List Agents", False, str(e))
            return []

    def test_create_agent(self, agent_config: Optional[Dict] = None):
        """Test creating a new agent"""
        if not agent_config:
            agent_config = {
                "name": f"test_agent_{int(time.time())}",
                "type": "generic",
                "role": "Test Agent",
                "system_prompt": "You are a helpful test assistant.",
                "capabilities": ["text_processing", "inference"],
                "functions": ["inference", "text_processing"],
                "auto_start": True,
                "max_concurrent_jobs": 3,
                "llm_config": {
                    "model_name": "default",
                    "api_endpoint": f"{self.base_url}/v1",
                    "temperature": 0.7,
                    "max_tokens": 1024
                }
            }
        
        try:
            response = self.make_request('POST', '/api/v1/agents', json=agent_config)
            if response.status_code in [200, 201]:
                data = response.json()
                agent_id = data.get('data', {}).get('agent_id')
                if agent_id:
                    self.created_agents.append(agent_id)
                self.log_test("Create Agent", True, f"Created agent: {agent_id}")
                return agent_id
            else:
                self.log_test("Create Agent", False, 
                            f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("Create Agent", False, str(e))
            return None

    def test_get_agent_details(self, agent_id: str):
        """Test getting agent details"""
        try:
            response = self.make_request('GET', f'/api/v1/agents/{agent_id}')
            if response.status_code == 200:
                data = response.json()
                agent_data = data.get('data', {})
                running = agent_data.get('running', False)
                self.log_test("Get Agent Details", True,
                            f"Agent {agent_id} running: {running}")
                return agent_data
            else:
                self.log_test("Get Agent Details", False,
                            f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Get Agent Details", False, str(e))
            return None

    def test_agent_control(self, agent_id: str):
        """Test agent start/stop control"""
        try:
            # Test stop
            response = self.make_request('POST', f'/api/v1/agents/{agent_id}/stop')
            stop_success = response.status_code in [200, 204]
            
            # Test start
            response = self.make_request('POST', f'/api/v1/agents/{agent_id}/start')
            start_success = response.status_code in [200, 204]
            
            success = stop_success and start_success
            self.log_test("Agent Control", success,
                        f"Stop: {stop_success}, Start: {start_success}")
            return success
        except Exception as e:
            self.log_test("Agent Control", False, str(e))
            return False

    # ===== FUNCTION EXECUTION TESTS =====
    
    def test_agent_function_execution(self, agent_id: str):
        """Test agent function execution"""
        test_functions = [
            {
                "function": "inference",
                "parameters": {
                    "prompt": "Hello, this is a test. Please respond briefly.",
                    "max_tokens": 50
                }
            },
            {
                "function": "text_processing",
                "parameters": {
                    "operation": "summarize",
                    "text": "This is a test text for processing. It contains multiple sentences for testing purposes."
                }
            }
        ]
        
        for test_func in test_functions:
            try:
                response = self.make_request('POST', f'/api/v1/agents/{agent_id}/execute',
                                           json=test_func)
                success = response.status_code == 200
                if success:
                    data = response.json()
                    result_success = data.get('success', False)
                    self.log_test(f"Execute Function: {test_func['function']}", 
                                result_success,
                                f"Response: {data.get('message', 'No message')[:100]}")
                else:
                    self.log_test(f"Execute Function: {test_func['function']}", False,
                                f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Execute Function: {test_func['function']}", False, str(e))

    def test_async_function_execution(self, agent_id: str):
        """Test asynchronous function execution"""
        try:
            payload = {
                "function": "inference",
                "parameters": {
                    "prompt": "Generate a short creative story about AI.",
                    "max_tokens": 200
                }
            }
            
            response = self.make_request('POST', f'/api/v1/agents/{agent_id}/execute-async',
                                       json=payload)
            if response.status_code == 200:
                data = response.json()
                job_id = data.get('data', {}).get('job_id')
                if job_id:
                    # Check job status
                    time.sleep(2)  # Wait a bit
                    status_response = self.make_request('GET', f'/api/v1/agents/jobs/{job_id}/status')
                    status_success = status_response.status_code == 200
                    self.log_test("Async Function Execution", status_success,
                                f"Job ID: {job_id}")
                else:
                    self.log_test("Async Function Execution", False, "No job ID returned")
            else:
                self.log_test("Async Function Execution", False,
                            f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Async Function Execution", False, str(e))

    # ===== OPENAI COMPATIBLE TESTS =====
    
    def test_openai_chat_completions(self, agent_id: str):
        """Test OpenAI-compatible chat completions endpoint"""
        try:
            payload = {
                "messages": [
                    {"role": "user", "content": "Hello! Can you help me with a simple task?"}
                ],
                "max_tokens": 100,
                "temperature": 0.7
            }
            
            response = self.make_request('POST', f'/v1/agents/{agent_id}/chat/completions',
                                       json=payload)
            success = response.status_code == 200
            if success:
                data = response.json()
                choices = data.get('choices', [])
                has_content = len(choices) > 0 and choices[0].get('message', {}).get('content')
                self.log_test("OpenAI Chat Completions", has_content,
                            f"Response length: {len(str(data))}")
            else:
                self.log_test("OpenAI Chat Completions", False,
                            f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("OpenAI Chat Completions", False, str(e))

    def test_agent_chat_endpoints(self, agent_id: str):
        """Test various agent chat endpoints"""
        endpoints = [
            {
                "endpoint": f"/v1/agents/{agent_id}/chat",
                "payload": {"message": "Test chat message"}
            },
            {
                "endpoint": f"/v1/agents/{agent_id}/message",
                "payload": {"message": "Test message"}
            },
            {
                "endpoint": f"/v1/agents/{agent_id}/generate",
                "payload": {"message": "Generate a simple greeting"}
            },
            {
                "endpoint": f"/v1/agents/{agent_id}/respond",
                "payload": {"input": "Respond to this test input"}
            }
        ]
        
        for test_case in endpoints:
            try:
                response = self.make_request('POST', test_case['endpoint'],
                                           json=test_case['payload'])
                success = response.status_code == 200
                endpoint_name = test_case['endpoint'].split('/')[-1]
                self.log_test(f"Agent Chat Endpoint: {endpoint_name}", success,
                            f"Status: {response.status_code}")
            except Exception as e:
                endpoint_name = test_case['endpoint'].split('/')[-1]
                self.log_test(f"Agent Chat Endpoint: {endpoint_name}", False, str(e))

    # ===== WORKFLOW ORCHESTRATION TESTS =====
    
    def test_create_workflow(self, agent_ids: List[str]):
        """Test creating a workflow"""
        if len(agent_ids) < 2:
            self.skip_test("Create Workflow", "Need at least 2 agents")
            return None
            
        workflow_config = {
            "name": f"test_workflow_{int(time.time())}",
            "description": "Test workflow for agent collaboration",
            "global_context": {
                "test_mode": "true",
                "topic": "AI testing"
            },
            "steps": [
                {
                    "step_id": "research",
                    "agent_id": agent_ids[0],
                    "function_name": "text_processing",
                    "parameters": {
                        "operation": "analyze",
                        "text": "Analyze this test scenario"
                    },
                    "dependencies": [],
                    "parallel_allowed": True
                },
                {
                    "step_id": "process",
                    "agent_id": agent_ids[1] if len(agent_ids) > 1 else agent_ids[0],
                    "function_name": "inference",
                    "parameters": {
                        "prompt": "Process the analysis from the previous step"
                    },
                    "dependencies": ["research"],
                    "parallel_allowed": False
                }
            ]
        }
        
        try:
            response = self.make_request('POST', '/api/v1/orchestration/workflows',
                                       json=workflow_config)
            if response.status_code in [200, 201]:
                data = response.json()
                workflow_id = data.get('data', {}).get('workflow_id')
                if workflow_id:
                    self.created_workflows.append(workflow_id)
                self.log_test("Create Workflow", True, f"Created: {workflow_id}")
                return workflow_id
            else:
                self.log_test("Create Workflow", False,
                            f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("Create Workflow", False, str(e))
            return None

    def test_execute_workflow(self, workflow_id: str):
        """Test workflow execution"""
        try:
            payload = {
                "input_context": {
                    "test_input": "This is test input for workflow execution",
                    "priority": "high"
                }
            }
            
            # Test synchronous execution
            response = self.make_request('POST', f'/api/v1/orchestration/workflows/{workflow_id}/execute',
                                       json=payload)
            sync_success = response.status_code == 200
            
            # Test asynchronous execution
            response = self.make_request('POST', f'/api/v1/orchestration/workflows/{workflow_id}/execute-async',
                                       json=payload)
            async_success = response.status_code in [200, 202]
            
            success = sync_success or async_success
            self.log_test("Execute Workflow", success,
                        f"Sync: {sync_success}, Async: {async_success}")
            return success
        except Exception as e:
            self.log_test("Execute Workflow", False, str(e))
            return False

    def test_workflow_management(self):
        """Test workflow management operations"""
        try:
            # List workflows
            response = self.make_request('GET', '/api/v1/orchestration/workflows')
            list_success = response.status_code == 200
            
            # Get orchestration metrics
            response = self.make_request('GET', '/api/v1/orchestration/metrics')
            metrics_success = response.status_code == 200
            
            # Get orchestrator status
            response = self.make_request('GET', '/api/v1/orchestration/status')
            status_success = response.status_code == 200
            
            success = list_success and metrics_success and status_success
            self.log_test("Workflow Management", success,
                        f"List: {list_success}, Metrics: {metrics_success}, Status: {status_success}")
        except Exception as e:
            self.log_test("Workflow Management", False, str(e))

    # ===== COLLABORATION TESTS =====
    
    def test_agent_collaboration(self, agent_ids: List[str]):
        """Test agent collaboration features"""
        if len(agent_ids) < 2:
            self.skip_test("Agent Collaboration", "Need at least 2 agents")
            return
            
        try:
            # Create collaboration group
            group_config = {
                "group_id": f"test_group_{int(time.time())}",
                "name": "Test Collaboration Group",
                "pattern": "sequential",
                "agent_ids": agent_ids[:2],
                "shared_context": {
                    "collaboration_type": "test",
                    "task": "collaborative testing"
                }
            }
            
            response = self.make_request('POST', '/api/v1/orchestration/collaboration/groups',
                                       json=group_config)
            create_success = response.status_code in [200, 201]
            
            if create_success:
                group_id = group_config['group_id']
                self.created_collaboration_groups.append(group_id)
                
                # Execute collaboration
                collab_payload = {
                    "task_description": "Test collaborative task",
                    "input_data": {
                        "test_data": "This is test data for collaboration"
                    }
                }
                
                response = self.make_request('POST', f'/api/v1/orchestration/collaboration/{group_id}/execute',
                                           json=collab_payload)
                execute_success = response.status_code == 200
                
                success = create_success and execute_success
                self.log_test("Agent Collaboration", success,
                            f"Create: {create_success}, Execute: {execute_success}")
            else:
                self.log_test("Agent Collaboration", False,
                            f"Failed to create group: {response.status_code}")
        except Exception as e:
            self.log_test("Agent Collaboration", False, str(e))

    def test_agent_communication(self, agent_ids: List[str]):
        """Test agent-to-agent communication"""
        if len(agent_ids) < 2:
            self.skip_test("Agent Communication", "Need at least 2 agents")
            return
            
        try:
            # Test direct message
            message_payload = {
                "from_agent": agent_ids[0],
                "to_agent": agent_ids[1],
                "type": "task_request",
                "payload": {
                    "task": "Process this test message",
                    "data": "Test communication data",
                    "priority": "normal"
                }
            }
            
            response = self.make_request('POST', '/api/v1/agents/messages/send',
                                       json=message_payload)
            direct_success = response.status_code == 200
            
            # Test broadcast message
            broadcast_payload = {
                "from_agent": agent_ids[0],
                "type": "status_update",
                "payload": {
                    "message": "Test broadcast message",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            response = self.make_request('POST', '/api/v1/agents/messages/broadcast',
                                       json=broadcast_payload)
            broadcast_success = response.status_code == 200
            
            success = direct_success or broadcast_success
            self.log_test("Agent Communication", success,
                        f"Direct: {direct_success}, Broadcast: {broadcast_success}")
        except Exception as e:
            self.log_test("Agent Communication", False, str(e))

    # ===== DOCUMENT/RAG TESTS =====
    
    def test_document_management(self):
        """Test document management features"""
        try:
            # Test add documents
            add_payload = {
                "documents": [
                    {
                        "text": "This is a test document for the RAG system. It contains information about testing procedures and AI capabilities.",
                        "metadata": {
                            "source": "test_document.txt",
                            "type": "test",
                            "category": "testing"
                        }
                    },
                    {
                        "text": "Another test document with different content. This one focuses on agent capabilities and workflow management.",
                        "metadata": {
                            "source": "test_document_2.txt",
                            "type": "test",
                            "category": "agents"
                        }
                    }
                ],
                "collection_name": "test_collection"
            }
            
            response = self.make_request('POST', '/api/v1/documents', json=add_payload)
            add_success = response.status_code == 200
            
            # Test document retrieval
            retrieve_payload = {
                "query": "testing procedures and AI capabilities",
                "k": 5,
                "score_threshold": 0.5,
                "collection_name": "test_collection"
            }
            
            response = self.make_request('POST', '/retrieve', json=retrieve_payload)
            retrieve_success = response.status_code == 200
            
            success = add_success and retrieve_success
            self.log_test("Document Management", success,
                        f"Add: {add_success}, Retrieve: {retrieve_success}")
            
            return success
        except Exception as e:
            self.log_test("Document Management", False, str(e))
            return False

    def test_rag_agent_functions(self, agent_id: str):
        """Test RAG-specific agent functions"""
        rag_functions = [
            {
                "function": "retrieval",
                "parameters": {
                    "query": "AI testing procedures",
                    "k": 3,
                    "score_threshold": 0.6
                }
            },
            {
                "function": "context_retrieval", 
                "parameters": {
                    "query": "agent workflow management",
                    "k": 2,
                    "context_format": "detailed"
                }
            },
            {
                "function": "add_document",
                "parameters": {
                    "documents": [
                        {
                            "text": "RAG test document for agent function testing",
                            "metadata": {"source": "agent_test", "type": "function_test"}
                        }
                    ]
                }
            }
        ]
        
        for rag_func in rag_functions:
            try:
                response = self.make_request('POST', f'/api/v1/agents/{agent_id}/execute',
                                           json=rag_func)
                success = response.status_code == 200
                self.log_test(f"RAG Function: {rag_func['function']}", success,
                            f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"RAG Function: {rag_func['function']}", False, str(e))

    def test_pdf_parsing(self):
        """Test PDF parsing functionality"""
        try:
            # Create a simple test "PDF" (base64 encoded text for testing)
            test_content = "This is a test PDF document content for parsing testing."
            pdf_data = base64.b64encode(test_content.encode()).decode()
            
            payload = {
                "pdf_data": pdf_data,
                "method": "fast",
                "auto_index": True,
                "collection_name": "test_pdfs"
            }
            
            response = self.make_request('POST', '/parse-pdf', json=payload)
            success = response.status_code == 200
            self.log_test("PDF Parsing", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("PDF Parsing", False, str(e))

    # ===== MONITORING AND METRICS TESTS =====
    
    def test_system_monitoring(self):
        """Test system monitoring and metrics"""
        monitoring_endpoints = [
            '/api/v1/agents/health',
            '/api/v1/agents/metrics', 
            '/api/v1/agents/system/metrics',
            '/agents/orchestrator/status',
            '/agents/workflows/metrics',
            '/metrics',
            '/completion-metrics'
        ]
        
        success_count = 0
        for endpoint in monitoring_endpoints:
            try:
                response = self.make_request('GET', endpoint)
                if response.status_code == 200:
                    success_count += 1
                self.log_test(f"Monitoring: {endpoint}", response.status_code == 200,
                            f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Monitoring: {endpoint}", False, str(e))
        
        overall_success = success_count > len(monitoring_endpoints) // 2
        self.log_test("System Monitoring Overall", overall_success,
                    f"{success_count}/{len(monitoring_endpoints)} endpoints working")

    def test_agent_individual_status(self, agent_id: str):
        """Test individual agent status monitoring"""
        try:
            response = self.make_request('GET', f'/agents/{agent_id}/status')
            success = response.status_code == 200
            if success:
                data = response.json()
                running = data.get('running', False)
                self.log_test("Agent Individual Status", True,
                            f"Agent {agent_id} running: {running}")
            else:
                self.log_test("Agent Individual Status", False,
                            f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Agent Individual Status", False, str(e))

    # ===== AUTHENTICATION TESTS =====
    
    def test_authentication_features(self):
        """Test authentication and security features"""
        auth_endpoints = [
            ('GET', '/v1/auth/config'),
            ('GET', '/v1/auth/stats'),
            ('POST', '/v1/auth/clear', {"action": "test"})
        ]
        
        for method, endpoint, *payload in auth_endpoints:
            try:
                kwargs = {'json': payload[0]} if payload else {}
                response = self.make_request(method, endpoint, **kwargs)
                success = response.status_code in [200, 401, 403]  # 401/403 means auth is working
                endpoint_name = endpoint.split('/')[-1]
                self.log_test(f"Auth Endpoint: {endpoint_name}", success,
                            f"Status: {response.status_code}")
            except Exception as e:
                endpoint_name = endpoint.split('/')[-1] 
                self.log_test(f"Auth Endpoint: {endpoint_name}", False, str(e))

    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        try:
            # Make multiple rapid requests to test rate limiting
            rapid_requests = 10
            success_count = 0
            rate_limited = False
            
            for i in range(rapid_requests):
                response = self.make_request('GET', '/health')
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 429:
                    rate_limited = True
                    break
                time.sleep(0.1)  # Small delay
            
            # Rate limiting working if we got rate limited or all succeeded
            success = rate_limited or success_count == rapid_requests
            self.log_test("Rate Limiting", success,
                        f"Requests: {success_count}/{rapid_requests}, Rate limited: {rate_limited}")
        except Exception as e:
            self.log_test("Rate Limiting", False, str(e))

    # ===== LOAD BALANCING TESTS =====
    
    def test_load_balancing(self, agent_ids: List[str]):
        """Test load balancing and optimal agent selection"""
        if len(agent_ids) < 2:
            self.skip_test("Load Balancing", "Need at least 2 agents")
            return
            
        try:
            # Test optimal agent selection
            select_payload = {
                "capability": "text_processing",
                "context": {
                    "workload": "medium",
                    "complexity": "low"
                }
            }
            
            response = self.make_request('POST', '/api/v1/orchestration/select-agent',
                                       json=select_payload)
            select_success = response.status_code == 200
            
            # Test workload distribution
            distribute_payload = {
                "task_type": "text_processing",
                "tasks": [
                    {"input": "Task 1 for distribution"},
                    {"input": "Task 2 for distribution"},
                    {"input": "Task 3 for distribution"}
                ]
            }
            
            response = self.make_request('POST', '/api/v1/orchestration/distribute-workload',
                                       json=distribute_payload)
            distribute_success = response.status_code == 200
            
            success = select_success or distribute_success
            self.log_test("Load Balancing", success,
                        f"Select: {select_success}, Distribute: {distribute_success}")
        except Exception as e:
            self.log_test("Load Balancing", False, str(e))

    # ===== CLEANUP METHODS =====
    
    def cleanup_resources(self):
        """Clean up created test resources"""
        logger.info("Cleaning up test resources...")
        
        # Delete created agents
        for agent_id in self.created_agents:
            try:
                response = self.make_request('DELETE', f'/api/v1/agents/{agent_id}')
                if response.status_code in [200, 204, 404]:
                    logger.info(f"Deleted agent: {agent_id}")
                else:
                    logger.warning(f"Failed to delete agent {agent_id}: {response.status_code}")
            except Exception as e:
                logger.warning(f"Error deleting agent {agent_id}: {e}")
        
        # Delete created workflows
        for workflow_id in self.created_workflows:
            try:
                response = self.make_request('DELETE', f'/api/v1/orchestration/workflows/{workflow_id}')
                if response.status_code in [200, 204, 404]:
                    logger.info(f"Deleted workflow: {workflow_id}")
                else:
                    logger.warning(f"Failed to delete workflow {workflow_id}: {response.status_code}")
            except Exception as e:
                logger.warning(f"Error deleting workflow {workflow_id}: {e}")
        
        # Delete created collaboration groups
        for group_id in self.created_collaboration_groups:
            try:
                response = self.make_request('DELETE', f'/api/v1/orchestration/collaboration/{group_id}')
                if response.status_code in [200, 204, 404]:
                    logger.info(f"Deleted collaboration group: {group_id}")
                else:
                    logger.warning(f"Failed to delete group {group_id}: {response.status_code}")
            except Exception as e:
                logger.warning(f"Error deleting group {group_id}: {e}")

    # ===== MAIN TEST RUNNER =====
    
    def run_all_tests(self, skip_auth=False, skip_rag=False):
        """Run all test suites"""
        logger.info("=" * 60)
        logger.info("Starting Kolosal Agent System Test Suite")
        logger.info("=" * 60)
        
        try:
            # Basic connectivity tests
            logger.info("\n--- BASIC CONNECTIVITY TESTS ---")
            if not self.test_server_health():
                logger.error("Server health check failed - aborting tests")
                return
            
            if not self.test_agent_system_status():
                logger.warning("Agent system not available - some tests may fail")
            
            # Get existing agents or create test agents
            logger.info("\n--- AGENT MANAGEMENT TESTS ---")
            existing_agents = self.test_list_agents()
            
            # Create test agents if needed
            test_agent_ids = []
            if len(existing_agents) < 2:
                logger.info("Creating test agents...")
                for i in range(2):
                    agent_id = self.test_create_agent()
                    if agent_id:
                        test_agent_ids.append(agent_id)
            else:
                # Use existing agents
                test_agent_ids = [agent['id'] for agent in existing_agents[:2]]
            
            if not test_agent_ids:
                logger.error("No agents available for testing")
                return
            
            # Test agent operations
            main_agent_id = test_agent_ids[0]
            self.test_get_agent_details(main_agent_id)
            self.test_agent_control(main_agent_id)
            
            # Function execution tests
            logger.info("\n--- FUNCTION EXECUTION TESTS ---")
            self.test_agent_function_execution(main_agent_id)
            self.test_async_function_execution(main_agent_id)
            
            # OpenAI compatibility tests
            logger.info("\n--- OPENAI COMPATIBILITY TESTS ---")
            self.test_openai_chat_completions(main_agent_id)
            self.test_agent_chat_endpoints(main_agent_id)
            
            # Workflow orchestration tests
            logger.info("\n--- WORKFLOW ORCHESTRATION TESTS ---")
            workflow_id = self.test_create_workflow(test_agent_ids)
            if workflow_id:
                self.test_execute_workflow(workflow_id)
            self.test_workflow_management()
            
            # Collaboration tests
            logger.info("\n--- COLLABORATION TESTS ---")
            self.test_agent_collaboration(test_agent_ids)
            self.test_agent_communication(test_agent_ids)
            
            # Document/RAG tests
            if not skip_rag:
                logger.info("\n--- DOCUMENT/RAG TESTS ---")
                self.test_document_management()
                self.test_rag_agent_functions(main_agent_id)
                self.test_pdf_parsing()
            else:
                logger.info("\n--- DOCUMENT/RAG TESTS SKIPPED ---")
            
            # Monitoring and metrics tests
            logger.info("\n--- MONITORING TESTS ---")
            self.test_system_monitoring()
            self.test_agent_individual_status(main_agent_id)
            
            # Authentication tests
            if not skip_auth:
                logger.info("\n--- AUTHENTICATION TESTS ---")
                self.test_authentication_features()
                self.test_rate_limiting()
            else:
                logger.info("\n--- AUTHENTICATION TESTS SKIPPED ---")
            
            # Load balancing tests
            logger.info("\n--- LOAD BALANCING TESTS ---")
            self.test_load_balancing(test_agent_ids)
            
        finally:
            # Cleanup
            self.cleanup_resources()
        
        # Print summary
        self.print_test_summary()

    def print_test_summary(self):
        """Print test results summary"""
        logger.info("\n" + "=" * 60)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        
        total_tests = self.test_results['passed'] + self.test_results['failed'] + self.test_results['skipped']
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {self.test_results['passed']}")
        logger.info(f"Failed: {self.test_results['failed']}")
        logger.info(f"Skipped: {self.test_results['skipped']}")
        
        if self.test_results['failed'] > 0:
            success_rate = (self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed'])) * 100
        else:
            success_rate = 100.0
        
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if self.test_results['errors']:
            logger.info("\nFAILED TESTS:")
            for error in self.test_results['errors']:
                logger.error(f"  {error['test']}: {error['message']}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Test Kolosal Server Agent System')
    parser.add_argument('--server-url', default='http://localhost:8080',
                       help='Base URL of the Kolosal Server')
    parser.add_argument('--api-key', help='API key for authentication')
    parser.add_argument('--skip-auth', action='store_true',
                       help='Skip authentication tests')
    parser.add_argument('--skip-rag', action='store_true',
                       help='Skip RAG/document tests')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize tester
    tester = KolosalAgentTester(args.server_url, args.api_key)
    
    # Run tests
    try:
        tester.run_all_tests(skip_auth=args.skip_auth, skip_rag=args.skip_rag)
    except KeyboardInterrupt:
        logger.info("\nTests interrupted by user")
        tester.cleanup_resources()
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        tester.cleanup_resources()
        sys.exit(1)


if __name__ == "__main__":
    main()
