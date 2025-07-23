#!/usr/bin/env pwsh
# PowerShell script to launch Kolosal Server tests
# Aligned with actual server configuration

param(
    [switch]$TestEndpoints,
    [switch]$RunTests,
    [switch]$Help
)

if ($Help) {
    Write-Host "Kolosal Server Test Launcher"
    Write-Host "Usage: .\launch_tests.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -TestEndpoints    Test endpoint availability only"
    Write-Host "  -RunTests        Run the full test suite"
    Write-Host "  -Help            Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\launch_tests.ps1 -TestEndpoints"
    Write-Host "  .\launch_tests.ps1 -RunTests"
    exit 0
}

Write-Host "=" * 60
Write-Host "KOLOSAL SERVER TEST LAUNCHER (PowerShell)"
Write-Host "=" * 60
Write-Host "Server URL: http://127.0.0.1:8080"
Write-Host "Expected Models: qwen3-0.6b, text-embedding-3-small"
Write-Host "=" * 60

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion"
} catch {
    Write-Host "❌ Python not found. Please install Python 3.7+ and add to PATH"
    exit 1
}

# Check if required files exist
$requiredFiles = @("main.py", "config.py", "launcher.py", "endpoint_tester.py")
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ Found: $file"
    } else {
        Write-Host "❌ Missing: $file"
        exit 1
    }
}

# Build Python command arguments
$pythonArgs = @("launcher.py")

if ($TestEndpoints) {
    $pythonArgs += "--test-endpoints"
}



if ($RunTests) {
    $pythonArgs += "--run-tests"
}

# If no specific action, show help
if (-not $TestEndpoints -and -not $RunTests) {
    Write-Host ""
    Write-Host "No action specified. Use one of the following:"
    Write-Host "  -TestEndpoints to check server endpoints"
    Write-Host "  -RunTests to run the full test suite"
    Write-Host "  -Help for more information"
    exit 0
}

Write-Host ""
Write-Host "🚀 Executing: python $($pythonArgs -join ' ')"
Write-Host ""

# Execute the Python launcher
try {
    & python @pythonArgs
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host ""
        Write-Host "✅ Command completed successfully"
    } else {
        Write-Host ""
        Write-Host "❌ Command completed with errors (exit code: $exitCode)"
    }
    
    exit $exitCode
} catch {
    Write-Host "❌ Failed to execute Python launcher: $($_.Exception.Message)"
    exit 1
}
