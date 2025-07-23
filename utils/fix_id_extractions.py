#!/usr/bin/env python3
"""
Script to update all ID extraction patterns in workflow test files.

This script fixes all instances of hardcoded ID extraction patterns and replaces them
with the new utility function.
"""

import re
import os


def update_workflow_id_extractions(file_path):
    """Update workflow ID extractions in a file."""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern for workflow_id extraction
    workflow_pattern = r"workflow_id = response\.json\(\)\.get\('data', \{\}\)\.get\('workflow_id'\)"
    replacement = "workflow_id = extract_id_from_response(response.json(), 'workflow')"
    
    content = re.sub(workflow_pattern, replacement, content)
    
    # Pattern for execution_id extraction
    execution_pattern = r"execution_id = response\.json\(\)\.get\('data', \{\}\)\.get\('execution_id'\)"
    replacement = "execution_id = extract_id_from_response(response.json(), 'execution')"
    
    content = re.sub(execution_pattern, replacement, content)
    
    # Pattern for job_id extraction (if any missed)
    job_pattern = r"job_id = data\.get\('data', \{\}\)\.get\('job_id'\)"
    replacement = "job_id = extract_id_from_response(data, 'job')"
    
    content = re.sub(job_pattern, replacement, content)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated ID extractions in {file_path}")


def main():
    """Update all workflow test files."""
    
    workflow_file = "tests/agent_tests/test_workflows.py"
    
    if os.path.exists(workflow_file):
        update_workflow_id_extractions(workflow_file)
    else:
        print(f"❌ File not found: {workflow_file}")
    
    print("\n✅ All ID extraction patterns updated!")
    print("📝 Changes made:")
    print("  - workflow_id extractions now use extract_id_from_response()")
    print("  - execution_id extractions now use extract_id_from_response()")
    print("  - Consistent error handling for missing IDs")


if __name__ == "__main__":
    main()
