#!/usr/bin/env python3
"""
Workflow-specific test suite for Kolosal Server.

This script focuses on testing workflow orchestration features including:
- Sequential workflows
- Parallel execution
- Pipeline patterns
- Consensus workflows
- Hierarchical workflows
- Negotiation patterns
- Complex multi-step workflows
- Workflow error handling and recovery

Usage:
    python test_workflows.py [options]
"""

import requests
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowTester:
    def __init__(self, base_url: str = "http://localhost:8080", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'X-API-Key': api_key
            })
        self.session.headers.update({'Content-Type': 'application/json'})
        self.created_workflows = []
        self.created_agents = []

    def create_test_agents(self, count: int = 3) -> List[str]:
        """Create test agents for workflow testing"""
        agent_ids = []
        
        agent_configs = [
            {
                "name": f"research_agent_{int(time.time())}",
                "type": "research",
                "role": "Research Specialist", 
                "system_prompt": "You are a research specialist. Analyze topics and gather information.",
                "capabilities": ["research", "analysis", "text_processing"],
                "functions": ["research", "analyze", "summarize"]
            },
            {
                "name": f"writer_agent_{int(time.time())}",
                "type": "content",
                "role": "Content Writer",
                "system_prompt": "You are a content writer. Create engaging content based on research.",
                "capabilities": ["writing", "content_creation", "editing"],
                "functions": ["write", "edit", "format"]
            },
            {
                "name": f"reviewer_agent_{int(time.time())}",
                "type": "review",
                "role": "Quality Reviewer",
                "system_prompt": "You are a quality reviewer. Review and improve content quality.",
                "capabilities": ["review", "quality_control", "editing"],
                "functions": ["review", "validate", "improve"]
            }
        ]
        
        for i in range(min(count, len(agent_configs))):
            try:
                response = self.session.post(f"{self.base_url}/api/v1/agents", 
                                           json=agent_configs[i])
                if response.status_code in [200, 201]:
                    data = response.json()
                    agent_id = data.get('data', {}).get('agent_id')
                    if agent_id:
                        agent_ids.append(agent_id)
                        self.created_agents.append(agent_id)
                        logger.info(f"Created agent: {agent_id}")
            except Exception as e:
                logger.error(f"Failed to create agent: {e}")
        
        return agent_ids

    def test_sequential_workflow(self, agent_ids: List[str]):
        """Test sequential workflow execution"""
        if len(agent_ids) < 3:
            logger.warning("Need at least 3 agents for sequential workflow")
            return False
            
        workflow_config = {
            "name": f"sequential_workflow_{int(time.time())}",
            "description": "Sequential content creation workflow",
            "type": "sequential",
            "global_context": {
                "topic": "AI in Modern Workplaces",
                "target_audience": "business professionals",
                "content_length": "medium"
            },
            "steps": [
                {
                    "step_id": "research",
                    "agent_id": agent_ids[0],
                    "function_name": "research",
                    "parameters": {
                        "topic": "${global_context.topic}",
                        "depth": "comprehensive",
                        "sources": ["academic", "industry"]
                    },
                    "dependencies": [],
                    "timeout": 120,
                    "retry_count": 2
                },
                {
                    "step_id": "write_draft",
                    "agent_id": agent_ids[1],
                    "function_name": "write",
                    "parameters": {
                        "content_type": "article",
                        "research_data": "${steps.research.output}",
                        "target_audience": "${global_context.target_audience}",
                        "length": "${global_context.content_length}"
                    },
                    "dependencies": ["research"],
                    "timeout": 180,
                    "retry_count": 1
                },
                {
                    "step_id": "review_content",
                    "agent_id": agent_ids[2],
                    "function_name": "review",
                    "parameters": {
                        "content": "${steps.write_draft.output}",
                        "criteria": ["accuracy", "clarity", "engagement"],
                        "feedback_detail": "detailed"
                    },
                    "dependencies": ["write_draft"],
                    "timeout": 120,
                    "retry_count": 1
                },
                {
                    "step_id": "finalize",
                    "agent_id": agent_ids[1],
                    "function_name": "edit",
                    "parameters": {
                        "content": "${steps.write_draft.output}",
                        "feedback": "${steps.review_content.output}",
                        "action": "incorporate_feedback"
                    },
                    "dependencies": ["review_content"],
                    "timeout": 120,
                    "retry_count": 1
                }
            ]
        }
        
        try:
            # Create workflow
            response = self.session.post(f"{self.base_url}/api/v1/orchestration/workflows",
                                       json=workflow_config)
            if response.status_code not in [200, 201]:
                logger.error(f"Failed to create sequential workflow: {response.status_code}")
                return False
                
            workflow_id = response.json().get('data', {}).get('workflow_id')
            self.created_workflows.append(workflow_id)
            
            # Execute workflow
            execution_payload = {
                "input_context": {
                    "workflow_type": "sequential_test",
                    "priority": "high",
                    "deadline": (datetime.now().timestamp() + 600)  # 10 minutes
                }
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/orchestration/workflows/{workflow_id}/execute",
                                       json=execution_payload)
            
            success = response.status_code == 200
            logger.info(f"Sequential workflow test: {'PASS' if success else 'FAIL'}")
            
            if success:
                result = response.json()
                logger.info(f"Workflow completed with {len(result.get('data', {}).get('steps', []))} steps")
            
            return success
            
        except Exception as e:
            logger.error(f"Sequential workflow test failed: {e}")
            return False

    def test_parallel_workflow(self, agent_ids: List[str]):
        """Test parallel workflow execution"""
        if len(agent_ids) < 3:
            logger.warning("Need at least 3 agents for parallel workflow")
            return False
            
        workflow_config = {
            "name": f"parallel_workflow_{int(time.time())}",
            "description": "Parallel research and analysis workflow",
            "type": "parallel",
            "global_context": {
                "research_topic": "Machine Learning Applications",
                "research_areas": ["healthcare", "finance", "manufacturing"]
            },
            "steps": [
                {
                    "step_id": "research_healthcare",
                    "agent_id": agent_ids[0],
                    "function_name": "research",
                    "parameters": {
                        "topic": "Machine Learning in Healthcare",
                        "focus": "applications and case studies",
                        "depth": "detailed"
                    },
                    "dependencies": [],
                    "parallel_allowed": True,
                    "timeout": 180
                },
                {
                    "step_id": "research_finance",
                    "agent_id": agent_ids[1],
                    "function_name": "research",
                    "parameters": {
                        "topic": "Machine Learning in Finance",
                        "focus": "applications and case studies",
                        "depth": "detailed"
                    },
                    "dependencies": [],
                    "parallel_allowed": True,
                    "timeout": 180
                },
                {
                    "step_id": "research_manufacturing",
                    "agent_id": agent_ids[2],
                    "function_name": "research",
                    "parameters": {
                        "topic": "Machine Learning in Manufacturing",
                        "focus": "applications and case studies", 
                        "depth": "detailed"
                    },
                    "dependencies": [],
                    "parallel_allowed": True,
                    "timeout": 180
                },
                {
                    "step_id": "synthesize_findings",
                    "agent_id": agent_ids[0],
                    "function_name": "analyze",
                    "parameters": {
                        "healthcare_data": "${steps.research_healthcare.output}",
                        "finance_data": "${steps.research_finance.output}",
                        "manufacturing_data": "${steps.research_manufacturing.output}",
                        "analysis_type": "comparative_synthesis"
                    },
                    "dependencies": ["research_healthcare", "research_finance", "research_manufacturing"],
                    "parallel_allowed": False,
                    "timeout": 240
                }
            ]
        }
        
        try:
            # Create workflow
            response = self.session.post(f"{self.base_url}/api/v1/orchestration/workflows",
                                       json=workflow_config)
            if response.status_code not in [200, 201]:
                logger.error(f"Failed to create parallel workflow: {response.status_code}")
                return False
                
            workflow_id = response.json().get('data', {}).get('workflow_id')
            self.created_workflows.append(workflow_id)
            
            # Execute workflow asynchronously to handle parallel execution
            execution_payload = {
                "input_context": {
                    "execution_mode": "parallel",
                    "max_parallel_steps": 3
                }
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/orchestration/workflows/{workflow_id}/execute-async",
                                       json=execution_payload)
            
            if response.status_code in [200, 202]:
                execution_id = response.json().get('data', {}).get('execution_id')
                logger.info(f"Parallel workflow started: {execution_id}")
                
                # Check status periodically
                for _ in range(10):  # Check for up to 2 minutes
                    time.sleep(12)
                    status_response = self.session.get(f"{self.base_url}/api/v1/orchestration/workflows/{workflow_id}/status")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data.get('data', {}).get('status')
                        if status in ['completed', 'failed']:
                            break
                
                success = status == 'completed'
                logger.info(f"Parallel workflow test: {'PASS' if success else 'FAIL'}")
                return success
            else:
                logger.error(f"Failed to execute parallel workflow: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Parallel workflow test failed: {e}")
            return False

    def test_pipeline_workflow(self, agent_ids: List[str]):
        """Test pipeline workflow with data transformation"""
        if len(agent_ids) < 2:
            logger.warning("Need at least 2 agents for pipeline workflow")
            return False
            
        workflow_config = {
            "name": f"pipeline_workflow_{int(time.time())}",
            "description": "Data processing pipeline workflow",
            "type": "pipeline",
            "global_context": {
                "data_source": "customer_feedback",
                "processing_stages": ["extract", "transform", "analyze", "report"]
            },
            "steps": [
                {
                    "step_id": "extract_data",
                    "agent_id": agent_ids[0],
                    "function_name": "text_processing",
                    "parameters": {
                        "operation": "extract",
                        "data_type": "customer_feedback",
                        "format": "structured"
                    },
                    "dependencies": [],
                    "output_format": "json",
                    "timeout": 60
                },
                {
                    "step_id": "transform_data",
                    "agent_id": agent_ids[0],
                    "function_name": "text_processing",
                    "parameters": {
                        "operation": "transform",
                        "input_data": "${steps.extract_data.output}",
                        "transformation_rules": ["normalize", "categorize", "sentiment_score"]
                    },
                    "dependencies": ["extract_data"],
                    "output_format": "json",
                    "timeout": 90
                },
                {
                    "step_id": "analyze_patterns",
                    "agent_id": agent_ids[1],
                    "function_name": "analyze",
                    "parameters": {
                        "data": "${steps.transform_data.output}",
                        "analysis_type": "pattern_detection",
                        "metrics": ["sentiment_trends", "topic_clusters", "urgency_levels"]
                    },
                    "dependencies": ["transform_data"],
                    "output_format": "json",
                    "timeout": 120
                },
                {
                    "step_id": "generate_report",
                    "agent_id": agent_ids[1],
                    "function_name": "write",
                    "parameters": {
                        "content_type": "analysis_report",
                        "analysis_data": "${steps.analyze_patterns.output}",
                        "report_sections": ["executive_summary", "key_findings", "recommendations"]
                    },
                    "dependencies": ["analyze_patterns"],
                    "output_format": "markdown",
                    "timeout": 150
                }
            ]
        }
        
        try:
            # Create workflow
            response = self.session.post(f"{self.base_url}/api/v1/orchestration/workflows",
                                       json=workflow_config)
            if response.status_code not in [200, 201]:
                logger.error(f"Failed to create pipeline workflow: {response.status_code}")
                return False
                
            workflow_id = response.json().get('data', {}).get('workflow_id')
            self.created_workflows.append(workflow_id)
            
            # Execute workflow
            execution_payload = {
                "input_context": {
                    "pipeline_mode": True,
                    "data_validation": True,
                    "intermediate_outputs": True
                }
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/orchestration/workflows/{workflow_id}/execute",
                                       json=execution_payload)
            
            success = response.status_code == 200
            logger.info(f"Pipeline workflow test: {'PASS' if success else 'FAIL'}")
            
            if success:
                result = response.json()
                pipeline_data = result.get('data', {})
                logger.info(f"Pipeline completed with {len(pipeline_data.get('steps', []))} stages")
            
            return success
            
        except Exception as e:
            logger.error(f"Pipeline workflow test failed: {e}")
            return False

    def test_consensus_workflow(self, agent_ids: List[str]):
        """Test consensus-based workflow"""
        if len(agent_ids) < 3:
            logger.warning("Need at least 3 agents for consensus workflow")
            return False
            
        workflow_config = {
            "name": f"consensus_workflow_{int(time.time())}",
            "description": "Multi-agent consensus decision workflow",
            "type": "consensus",
            "consensus_config": {
                "threshold": 0.67,  # 67% agreement required
                "max_rounds": 3,
                "voting_method": "weighted",
                "conflict_resolution": "negotiation"
            },
            "global_context": {
                "decision_topic": "Best AI Framework for Project",
                "criteria": ["performance", "ease_of_use", "community_support", "cost"]
            },
            "steps": [
                {
                    "step_id": "individual_evaluation_1",
                    "agent_id": agent_ids[0],
                    "function_name": "analyze",
                    "parameters": {
                        "topic": "${global_context.decision_topic}",
                        "criteria": "${global_context.criteria}",
                        "perspective": "technical_performance",
                        "output_format": "evaluation_matrix"
                    },
                    "dependencies": [],
                    "voting_weight": 1.0,
                    "timeout": 120
                },
                {
                    "step_id": "individual_evaluation_2",
                    "agent_id": agent_ids[1],
                    "function_name": "analyze",
                    "parameters": {
                        "topic": "${global_context.decision_topic}",
                        "criteria": "${global_context.criteria}",
                        "perspective": "business_value",
                        "output_format": "evaluation_matrix"
                    },
                    "dependencies": [],
                    "voting_weight": 1.0,
                    "timeout": 120
                },
                {
                    "step_id": "individual_evaluation_3",
                    "agent_id": agent_ids[2],
                    "function_name": "analyze",
                    "parameters": {
                        "topic": "${global_context.decision_topic}",
                        "criteria": "${global_context.criteria}",
                        "perspective": "implementation_feasibility",
                        "output_format": "evaluation_matrix"
                    },
                    "dependencies": [],
                    "voting_weight": 1.0,
                    "timeout": 120
                },
                {
                    "step_id": "consensus_building",
                    "agent_id": agent_ids[0],
                    "function_name": "analyze",
                    "parameters": {
                        "evaluation_1": "${steps.individual_evaluation_1.output}",
                        "evaluation_2": "${steps.individual_evaluation_2.output}",
                        "evaluation_3": "${steps.individual_evaluation_3.output}",
                        "consensus_method": "weighted_average",
                        "conflict_identification": True
                    },
                    "dependencies": ["individual_evaluation_1", "individual_evaluation_2", "individual_evaluation_3"],
                    "consensus_step": True,
                    "timeout": 180
                }
            ]
        }
        
        try:
            # Create workflow
            response = self.session.post(f"{self.base_url}/api/v1/orchestration/workflows",
                                       json=workflow_config)
            if response.status_code not in [200, 201]:
                logger.error(f"Failed to create consensus workflow: {response.status_code}")
                return False
                
            workflow_id = response.json().get('data', {}).get('workflow_id')
            self.created_workflows.append(workflow_id)
            
            # Execute workflow
            execution_payload = {
                "input_context": {
                    "consensus_mode": True,
                    "require_unanimous": False,
                    "allow_revisions": True
                }
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/orchestration/workflows/{workflow_id}/execute",
                                       json=execution_payload)
            
            success = response.status_code == 200
            logger.info(f"Consensus workflow test: {'PASS' if success else 'FAIL'}")
            
            if success:
                result = response.json()
                consensus_data = result.get('data', {})
                consensus_reached = consensus_data.get('consensus_reached', False)
                logger.info(f"Consensus reached: {consensus_reached}")
            
            return success
            
        except Exception as e:
            logger.error(f"Consensus workflow test failed: {e}")
            return False

    def test_error_handling_workflow(self, agent_ids: List[str]):
        """Test workflow error handling and recovery"""
        if len(agent_ids) < 2:
            logger.warning("Need at least 2 agents for error handling test")
            return False
            
        workflow_config = {
            "name": f"error_handling_workflow_{int(time.time())}",
            "description": "Workflow with deliberate errors for testing recovery",
            "error_handling": {
                "strategy": "retry_with_fallback",
                "max_retries": 2,
                "fallback_enabled": True,
                "continue_on_error": True
            },
            "steps": [
                {
                    "step_id": "normal_step",
                    "agent_id": agent_ids[0],
                    "function_name": "text_processing",
                    "parameters": {
                        "operation": "summarize",
                        "text": "This is a normal processing step that should succeed."
                    },
                    "dependencies": [],
                    "timeout": 60
                },
                {
                    "step_id": "error_prone_step",
                    "agent_id": agent_ids[1],
                    "function_name": "invalid_function",  # This should cause an error
                    "parameters": {
                        "invalid_param": "this will fail"
                    },
                    "dependencies": ["normal_step"],
                    "timeout": 30,
                    "retry_count": 2,
                    "fallback_step": "fallback_step"
                },
                {
                    "step_id": "fallback_step",
                    "agent_id": agent_ids[0],
                    "function_name": "text_processing",
                    "parameters": {
                        "operation": "process",
                        "text": "Fallback processing when error occurs"
                    },
                    "dependencies": [],
                    "is_fallback": True,
                    "timeout": 60
                },
                {
                    "step_id": "recovery_step",
                    "agent_id": agent_ids[0],
                    "function_name": "analyze",
                    "parameters": {
                        "data": "${steps.normal_step.output} ${steps.fallback_step.output}",
                        "analysis_type": "error_recovery_analysis"
                    },
                    "dependencies": ["fallback_step"],
                    "timeout": 90
                }
            ]
        }
        
        try:
            # Create workflow
            response = self.session.post(f"{self.base_url}/api/v1/orchestration/workflows",
                                       json=workflow_config)
            if response.status_code not in [200, 201]:
                logger.error(f"Failed to create error handling workflow: {response.status_code}")
                return False
                
            workflow_id = response.json().get('data', {}).get('workflow_id')
            self.created_workflows.append(workflow_id)
            
            # Execute workflow
            execution_payload = {
                "input_context": {
                    "error_testing": True,
                    "expected_errors": ["invalid_function"],
                    "recovery_mode": "automatic"
                }
            }
            
            response = self.session.post(f"{self.base_url}/api/v1/orchestration/workflows/{workflow_id}/execute",
                                       json=execution_payload)
            
            # For error handling test, we expect either success with recovery or partial completion
            success = response.status_code in [200, 206]  # 206 = Partial Content
            logger.info(f"Error handling workflow test: {'PASS' if success else 'FAIL'}")
            
            if success:
                result = response.json()
                error_data = result.get('data', {})
                errors_handled = error_data.get('errors_handled', 0)
                fallbacks_used = error_data.get('fallbacks_used', 0)
                logger.info(f"Errors handled: {errors_handled}, Fallbacks used: {fallbacks_used}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error handling workflow test failed: {e}")
            return False

    def test_workflow_monitoring(self):
        """Test workflow monitoring and metrics"""
        try:
            # Test workflow list
            response = self.session.get(f"{self.base_url}/api/v1/orchestration/workflows")
            list_success = response.status_code == 200
            
            # Test orchestration metrics
            response = self.session.get(f"{self.base_url}/api/v1/orchestration/metrics")
            metrics_success = response.status_code == 200
            
            # Test orchestrator status
            response = self.session.get(f"{self.base_url}/api/v1/orchestration/status")
            status_success = response.status_code == 200
            
            # Test workflow execution history
            response = self.session.get(f"{self.base_url}/api/v1/orchestration/workflows/history")
            history_success = response.status_code == 200
            
            success = list_success and metrics_success and status_success
            logger.info(f"Workflow monitoring test: {'PASS' if success else 'FAIL'}")
            logger.info(f"List: {list_success}, Metrics: {metrics_success}, Status: {status_success}, History: {history_success}")
            
            return success
            
        except Exception as e:
            logger.error(f"Workflow monitoring test failed: {e}")
            return False

    def cleanup(self):
        """Clean up created resources"""
        logger.info("Cleaning up workflow test resources...")
        
        # Delete workflows
        for workflow_id in self.created_workflows:
            try:
                response = self.session.delete(f"{self.base_url}/api/v1/orchestration/workflows/{workflow_id}")
                if response.status_code in [200, 204, 404]:
                    logger.info(f"Deleted workflow: {workflow_id}")
            except Exception as e:
                logger.warning(f"Error deleting workflow {workflow_id}: {e}")
        
        # Delete agents
        for agent_id in self.created_agents:
            try:
                response = self.session.delete(f"{self.base_url}/api/v1/agents/{agent_id}")
                if response.status_code in [200, 204, 404]:
                    logger.info(f"Deleted agent: {agent_id}")
            except Exception as e:
                logger.warning(f"Error deleting agent {agent_id}: {e}")

    def run_all_workflow_tests(self):
        """Run all workflow tests"""
        logger.info("=" * 60)
        logger.info("Starting Kolosal Workflow Test Suite")
        logger.info("=" * 60)
        
        try:
            # Create test agents
            logger.info("Creating test agents...")
            agent_ids = self.create_test_agents(3)
            
            if len(agent_ids) < 2:
                logger.error("Insufficient agents created for workflow testing")
                return
            
            logger.info(f"Created {len(agent_ids)} test agents")
            
            # Run workflow tests
            test_results = {
                'sequential': self.test_sequential_workflow(agent_ids),
                'parallel': self.test_parallel_workflow(agent_ids),
                'pipeline': self.test_pipeline_workflow(agent_ids),
                'consensus': self.test_consensus_workflow(agent_ids),
                'error_handling': self.test_error_handling_workflow(agent_ids),
                'monitoring': self.test_workflow_monitoring()
            }
            
            # Print results
            logger.info("\n" + "=" * 60)
            logger.info("WORKFLOW TEST RESULTS")
            logger.info("=" * 60)
            
            passed = sum(1 for result in test_results.values() if result)
            total = len(test_results)
            
            for test_name, result in test_results.items():
                status = "PASS" if result else "FAIL"
                logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
            
            logger.info(f"\nPassed: {passed}/{total}")
            logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
            
        finally:
            self.cleanup()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Kolosal Server Workflow System')
    parser.add_argument('--server-url', default='http://localhost:8080',
                       help='Base URL of the Kolosal Server')
    parser.add_argument('--api-key', help='API key for authentication')
    
    args = parser.parse_args()
    
    tester = WorkflowTester(args.server_url, args.api_key)
    tester.run_all_workflow_tests()


if __name__ == "__main__":
    main()
