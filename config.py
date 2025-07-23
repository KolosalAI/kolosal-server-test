"""
Configuration settings for Kolosal Server Test Suite.

This file contains all the configuration settings that align with the actual
Kolosal Server deployment, as observed from the server log output.
"""

# ===== SERVER CONFIGURATION =====
# Based on actual Kolosal Server configuration from server log

SERVER_CONFIG = {
    # Server connection details (from server log: "127.0.0.1:8080")
    "base_url": "http://127.0.0.1:8080",
    "host": "127.0.0.1",
    "port": 8080,
    
    # Authentication settings (from server log: "API Key Required: No")
    "api_key": None,  # Not required as per server config
    "auth_enabled": True,  # Auth is enabled but key not required
    
    # Rate limiting (from server log: "Max Requests: 100, Window: 60s")
    "rate_limit": {
        "max_requests": 100,
        "window_seconds": 60
    },
    
    # Timeouts (from server log: "Idle Timeout: 300s")
    "idle_timeout": 300,
    "request_timeout": 30,
    
    # CORS settings (from server log: "CORS: Enabled, Origins: 1 configured")
    "cors_enabled": True,
    "cors_origins": 1,
    
    # Public access (from server log: "Public Access: Disabled")
    "public_access": False,
    "internet_access": False
}

# ===== MODEL CONFIGURATION =====
# Based on models configured in the server log

MODELS = {
    # Primary LLM model (from server log)
    "primary_llm": "qwen3-0.6b",
    "model_path": "./downloads/Qwen3-0.6B-UD-Q4_K_XL.gguf",
    
    # Alternative LLM model (from server log, same file)
    "alt_llm": "gpt-3.5-turbo",
    "alt_model_path": "./downloads/Qwen3-0.6B-UD-Q4_K_XL.gguf",
    
    # Embedding models (from server log)
    "embedding_small": "text-embedding-3-small",
    "embedding_large": "text-embedding-3-large",
    "embedding_path": "./downloads/Qwen3-Embedding-0.6B-Q8_0.gguf",
    
    # Model loading settings (from server log: "Load immediately: No")
    "auto_load": False,
    "gpu_id": 0
}

# ===== AVAILABLE ENDPOINTS =====
# Based on the Kolosal Server API Usage Guide

ENDPOINTS = {
    # Core chat and completion endpoints
    "chat": "/chat",
    "completions": "/v1/completions", 
    "chat_completions": "/v1/chat/completions",
    "embeddings": "/v1/embeddings",
    
    # Document management endpoints
    "documents": "/documents",
    "document_upload": "/documents/upload",
    "search": "/search",
    "search_advanced": "/search/advanced",
    
    # Workflow endpoints
    "workflows": "/workflows",
    "workflow_execute": "/workflows/{id}/execute",
    
    # Session management endpoints
    "session_history": "/sessions/{id}/history",
    "session_clear": "/sessions/{id}/clear",
    
    # Legacy/alternative endpoints (may not be available)
    "health": "/health",
    "models": "/models",
    "engines": "/engines",
    
    # Vector & Document endpoints (legacy)
    "vector_search": "/vector-search",
    "retrieve": "/retrieve",
    "parse_pdf": "/parse-pdf",
    "parse_docx": "/parse-docx",
    
    # Agent System endpoints (may not be available in basic setup)
    "agents": "/agents",
    "agents_health": "/agents/health", 
    "agents_metrics": "/agents/metrics",
    
    # Authentication endpoints (may not be available)
    "auth_config": "/v1/auth/config",
    "auth_stats": "/v1/auth/stats",
    "auth_clear": "/v1/auth/clear",
    
    # Metrics endpoints
    "metrics": "/metrics",
    "system_metrics": "/system/metrics",
    "completion_metrics": "/completion-metrics"
}

# ===== FEATURES CONFIGURATION =====
# Based on server log feature listing

FEATURES = {
    "health_check": True,
    "metrics": True,
    "search_functionality": True,
    "internet_search": True,
    "system_metrics_monitoring": True,
    "workflows": True,
    "agent_system": True,
    "document_processing": True,
    "vector_search": True,
    "authentication": True,
    "rate_limiting": True,
    "cors": True
}

# ===== AGENT SYSTEM CONFIGURATION =====
# Based on agent configuration from server log

AGENT_SYSTEM = {
    # Agent configuration file
    "config_file": "config/agents.yaml",
    
    # From server log: "Found 9 agent configurations"
    "total_agents": 9,
    "total_functions": 13,
    "inference_engines": 3,
    
    # Known agents from server log
    "agents": [
        "research_assistant",
        "code_assistant", 
        "data_analyst",
        "document_manager",
        "content_creator",
        "project_manager",
        "qa_specialist",
        "response_test_agent",
        "knowledge_agent"
    ],
    
    # Available functions from server log
    "builtin_functions": [
        "add", "echo", "delay", "text_analysis", "text_processing",
        "data_transform", "data_analysis", "inference", "retrieval",
        "context_retrieval", "list_tools", "web_search", "code_generation",
        "add_document", "remove_document", "parse_pdf", "parse_docx",
        "get_embedding", "test_document_service"
    ]
}

# ===== TEST CONFIGURATION =====
# Settings for the test suite itself

TEST_CONFIG = {
    # Test file locations
    "test_files_dir": "test_files",
    "pdf_files": [
        "test_pdf.pdf", "test_pdf1.pdf", "test_pdf2.pdf", 
        "test_pdf3.pdf", "test_pdf4.pdf", "test_pdf5.pdf"
    ],
    "docx_files": [
        "test_docx.docx", "test_docx1.docx", "test_docx2.docx",
        "test_docx3.docx", "test_docx4.docx", "test_docx5.docx"
    ],
    
    # Test parameters
    "default_temperature": 0.7,
    "default_max_tokens": 128,
    "concurrent_requests": 5,
    "test_timeout": 30,
    
    # Test categories
    "categories": [
        "Engine Tests",
        "Document Processing", 
        "Document Ingestion",
        "Document Retrieval",
        "Agent System",
        "Workflow Tests",
        "Authentication Tests"
    ]
}

# ===== LOGGING CONFIGURATION =====
# Based on server log configuration

LOGGING_CONFIG = {
    "level": "INFO",
    "file": "Console",  # From server log: "File: Console"
    "access_log": False,  # From server log: "Access Log: Disabled"
    "details": True,
    "quiet": False
}

# Helper function to get full URL
def get_full_url(endpoint_key: str) -> str:
    """Get full URL for an endpoint."""
    base_url = SERVER_CONFIG["base_url"]
    endpoint = ENDPOINTS.get(endpoint_key, "")
    return f"{base_url}{endpoint}"

# Helper function to get model configuration
def get_model_config(model_type: str) -> dict:
    """Get model configuration by type."""
    model_configs = {
        "primary_llm": {
            "name": MODELS["primary_llm"],
            "path": MODELS["model_path"]
        },
        "alt_llm": {
            "name": MODELS["alt_llm"], 
            "path": MODELS["alt_model_path"]
        },
        "embedding_small": {
            "name": MODELS["embedding_small"],
            "path": MODELS["embedding_path"]
        },
        "embedding_large": {
            "name": MODELS["embedding_large"],
            "path": MODELS["embedding_path"]
        }
    }
    return model_configs.get(model_type, {})
