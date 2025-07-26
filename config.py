"""
Configuration settings for Kolosal Server Test Suite.

This file loads configuration settings from YAML files in the config/ directory
and provides backwards compatibility with the existing test infrastructure.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

# Configuration file paths
CONFIG_DIR = Path(__file__).parent / "config"
MAIN_CONFIG_FILE = CONFIG_DIR / "config.yaml"
AGENTS_CONFIG_FILE = CONFIG_DIR / "agents.yaml"
WORKFLOWS_CONFIG_FILE = CONFIG_DIR / "sequential_workflows.yaml"

class ConfigManager:
    """Manages loading and accessing configuration from YAML files."""
    
    def __init__(self):
        self._config = {}
        self._agents_config = {}
        self._workflows_config = {}
        self.load_configurations()
    
    def load_configurations(self):
        """Load all YAML configuration files."""
        try:
            # Load main configuration
            if MAIN_CONFIG_FILE.exists():
                with open(MAIN_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
            
            # Load agents configuration
            if AGENTS_CONFIG_FILE.exists():
                with open(AGENTS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self._agents_config = yaml.safe_load(f) or {}
            
            # Load workflows configuration
            if WORKFLOWS_CONFIG_FILE.exists():
                with open(WORKFLOWS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self._workflows_config = yaml.safe_load(f) or {}
                    
        except Exception as e:
            print(f"Warning: Error loading configuration files: {e}")
            print("Using default configuration values.")
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get main configuration."""
        return self._config
    
    @property
    def agents_config(self) -> Dict[str, Any]:
        """Get agents configuration."""
        return self._agents_config
    
    @property
    def workflows_config(self) -> Dict[str, Any]:
        """Get workflows configuration."""
        return self._workflows_config

# Initialize configuration manager
config_manager = ConfigManager()

# ===== SERVER CONFIGURATION =====
# Loaded from config/config.yaml with fallback defaults

def get_server_config() -> Dict[str, Any]:
    """Get server configuration from YAML with fallback defaults."""
    server_config = config_manager.config.get('server', {})
    
    # Build base URL
    host = server_config.get('host', '127.0.0.1')
    port = server_config.get('port', 8080)
    
    # For client connections, use localhost/127.0.0.1 instead of 0.0.0.0
    client_host = '127.0.0.1' if host == '0.0.0.0' else host
    base_url = f"http://{client_host}:{port}"
    
    return {
        "base_url": base_url,
        "host": host,  # Original host for server binding
        "client_host": client_host,  # Host for client connections
        "port": port,
        "api_key": None,  # Will be set if auth.api_keys are configured
        "auth_enabled": config_manager.config.get('auth', {}).get('enabled', True),
        "rate_limit": {
            "max_requests": config_manager.config.get('auth', {}).get('rate_limit', {}).get('max_requests', 100),
            "window_seconds": config_manager.config.get('auth', {}).get('rate_limit', {}).get('window_size', 60)
        },
        "idle_timeout": server_config.get('idle_timeout', 300),
        "request_timeout": 30,
        "cors_enabled": config_manager.config.get('auth', {}).get('cors', {}).get('enabled', True),
        "cors_origins": len(config_manager.config.get('auth', {}).get('cors', {}).get('allowed_origins', ['*'])),
        "public_access": server_config.get('allow_public_access', False),
        "internet_access": server_config.get('allow_internet_access', False)
    }

SERVER_CONFIG = get_server_config()

# ===== MODEL CONFIGURATION =====
# Loaded from config/config.yaml models section

def get_models_config() -> Dict[str, Any]:
    """Get models configuration from YAML with fallback defaults."""
    models_list = config_manager.config.get('models', [])
    
    # Find primary models
    primary_llm = None
    alt_llm = None
    embedding_small = None
    embedding_large = None
    
    for model in models_list:
        model_id = model.get('id', '')
        model_type = model.get('type', '')
        
        if model_id == 'qwen3-0.6b' and model_type == 'llm':
            primary_llm = model
        elif model_id == 'gpt-3.5-turbo' and model_type == 'llm':
            alt_llm = model
        elif model_id == 'text-embedding-3-small' and model_type == 'embedding':
            embedding_small = model
        elif model_id == 'text-embedding-3-large' and model_type == 'embedding':
            embedding_large = model
    
    return {
        "primary_llm": primary_llm.get('id', 'qwen3-0.6b') if primary_llm else 'qwen3-0.6b',
        "model_path": primary_llm.get('path', './downloads/Qwen3-0.6B-UD-Q4_K_XL.gguf') if primary_llm else './downloads/Qwen3-0.6B-UD-Q4_K_XL.gguf',
        "alt_llm": alt_llm.get('id', 'gpt-3.5-turbo') if alt_llm else 'gpt-3.5-turbo',
        "alt_model_path": alt_llm.get('path', './downloads/Qwen3-0.6B-UD-Q4_K_XL.gguf') if alt_llm else './downloads/Qwen3-0.6B-UD-Q4_K_XL.gguf',
        "embedding_small": embedding_small.get('id', 'text-embedding-3-small') if embedding_small else 'text-embedding-3-small',
        "embedding_large": embedding_large.get('id', 'text-embedding-3-large') if embedding_large else 'text-embedding-3-large',
        "embedding_path": embedding_small.get('path', './downloads/Qwen3-Embedding-0.6B-Q8_0.gguf') if embedding_small else './downloads/Qwen3-Embedding-0.6B-Q8_0.gguf',
        "auto_load": primary_llm.get('load_immediately', False) if primary_llm else False,
        "gpu_id": primary_llm.get('main_gpu_id', 0) if primary_llm else 0
    }

MODELS = get_models_config()

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
# Loaded from config/config.yaml features section

def get_features_config() -> Dict[str, bool]:
    """Get features configuration from YAML with fallback defaults."""
    features = config_manager.config.get('features', {})
    
    return {
        "health_check": features.get('health_check', True),
        "metrics": features.get('metrics', True),
        "search_functionality": config_manager.config.get('search', {}).get('enabled', True),
        "internet_search": config_manager.config.get('search', {}).get('enabled', True),
        "system_metrics_monitoring": features.get('metrics', True),
        "workflows": True,  # Always enabled if agents.yaml exists
        "agent_system": bool(config_manager.agents_config),
        "document_processing": config_manager.config.get('database', {}).get('qdrant', {}).get('enabled', True),
        "vector_search": config_manager.config.get('database', {}).get('qdrant', {}).get('enabled', True),
        "authentication": config_manager.config.get('auth', {}).get('enabled', True),
        "rate_limiting": config_manager.config.get('auth', {}).get('rate_limit', {}).get('enabled', True),
        "cors": config_manager.config.get('auth', {}).get('cors', {}).get('enabled', True)
    }

FEATURES = get_features_config()

# ===== AGENT SYSTEM CONFIGURATION =====
# Loaded from config/agents.yaml

def get_agent_system_config() -> Dict[str, Any]:
    """Get agent system configuration from YAML with fallback defaults."""
    agents_config = config_manager.agents_config
    
    if not agents_config:
        return {
            "config_file": "config/agents.yaml",
            "total_agents": 0,
            "total_functions": 0,
            "inference_engines": 0,
            "agents": [],
            "builtin_functions": []
        }
    
    # Extract agent names
    agents = []
    if 'agents' in agents_config:
        agents = [agent.get('agent_id', f'agent_{i}') for i, agent in enumerate(agents_config['agents'])]
    
    # Extract function names
    builtin_functions = []
    if 'builtin_functions' in agents_config:
        builtin_functions = list(agents_config['builtin_functions'].keys())
    
    # Count inference engines
    inference_engines = len(agents_config.get('inference_engines', []))
    
    return {
        "config_file": "config/agents.yaml",
        "total_agents": len(agents),
        "total_functions": len(builtin_functions),
        "inference_engines": inference_engines,
        "agents": agents,
        "builtin_functions": builtin_functions
    }

AGENT_SYSTEM = get_agent_system_config()

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
# Loaded from config/config.yaml logging section

def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration from YAML with fallback defaults."""
    logging_config = config_manager.config.get('logging', {})
    
    return {
        "level": logging_config.get('level', 'INFO'),
        "file": logging_config.get('file', 'Console'),
        "access_log": logging_config.get('access_log', False),
        "details": logging_config.get('show_request_details', True),
        "quiet": logging_config.get('quiet_mode', False)
    }

LOGGING_CONFIG = get_logging_config()

# Additional helper functions for YAML-based configuration

def get_workflow_config(workflow_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific workflow configuration by ID."""
    workflows = config_manager.workflows_config
    return workflows.get(workflow_id)

def get_available_workflows() -> List[str]:
    """Get list of available workflow IDs."""
    return list(config_manager.workflows_config.keys())

def get_inference_engines() -> List[Dict[str, Any]]:
    """Get list of configured inference engines."""
    return config_manager.agents_config.get('inference_engines', [])

def get_database_config() -> Dict[str, Any]:
    """Get database configuration."""
    return config_manager.config.get('database', {})

def get_search_config() -> Dict[str, Any]:
    """Get search configuration."""
    return config_manager.config.get('search', {})

def reload_configuration():
    """Reload all configuration files."""
    global config_manager, SERVER_CONFIG, MODELS, FEATURES, AGENT_SYSTEM, LOGGING_CONFIG
    config_manager.load_configurations()
    SERVER_CONFIG = get_server_config()
    MODELS = get_models_config()
    FEATURES = get_features_config()
    AGENT_SYSTEM = get_agent_system_config()
    LOGGING_CONFIG = get_logging_config()

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
