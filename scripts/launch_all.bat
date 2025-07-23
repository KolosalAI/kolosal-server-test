@echo off
setlocal enabledelayedexpansion

echo ===============================================
echo KOLOSAL SERVER TEST SUITE LAUNCHER
echo ===============================================
echo Configuration: Updated for server on 127.0.0.1:8080
echo Authentication: API Key not required
echo Models: qwen3-0.6b, text-embedding-3-small
echo ===============================================

REM Load .env variables if file exists
if exist ".env" (
    echo Loading environment variables from .env...
    for /f "tokens=1,* delims==" %%a in ('type ".env"') do (
        set "%%a=%%b"
    )
) else (
    echo Warning: .env file not found. Using default paths.
    REM Set default values
    set "QDRANT_SERVER_PATH=."
    set "QDRANT_PORT_1=6333"
    set "QDRANT_PORT_2=6334"
    set "QDRANT_VOLUME_PATH=./qdrant_storage"
    set "KOLOSAL_SERVER_PATH=../kolosal-server"
    set "KOLOSAL_EXE_PATH=./build/debug/kolosal-server.exe"
    set "TEST_SERVER_PATH=."
    set "VENV_ACTIVATE_PATH=.venv/Scripts/activate.ps1"
    set "TEST_RUN_COMMAND=echo Running tests..."
)

echo.
echo Starting services...
echo.

REM Start Qdrant in Docker
echo Starting Qdrant server on ports !QDRANT_PORT_1! and !QDRANT_PORT_2!...
start "Qdrant" powershell -NoExit -Command ^
"cd '!QDRANT_SERVER_PATH!'; docker run -p !QDRANT_PORT_1!:!QDRANT_PORT_1! -p !QDRANT_PORT_2!:!QDRANT_PORT_2! -v '!QDRANT_VOLUME_PATH!:/qdrant/storage' qdrant/qdrant; Start-Sleep -Seconds 3"

REM Wait for Qdrant to start
timeout /t 5 /nobreak >nul

REM Run kolosal-server.exe
echo Starting Kolosal Server at 127.0.0.1:8080...
start "Kolosal Server" powershell -NoExit -Command ^
"cd '!KOLOSAL_SERVER_PATH!'; .\!KOLOSAL_EXE_PATH!; Start-Sleep -Seconds 3"

REM Wait for Kolosal Server to start
timeout /t 10 /nobreak >nul

REM Run test script with virtual environment
echo Starting test suite...
start "Kolosal Test" powershell -NoExit -Command ^
"cd '!TEST_SERVER_PATH!'; if (Test-Path '!VENV_ACTIVATE_PATH!') { .\!VENV_ACTIVATE_PATH! }; python launcher.py --run-tests"

echo.
echo All services started! Check the opened terminal windows.
echo - Qdrant: Vector database on ports !QDRANT_PORT_1!/!QDRANT_PORT_2!
echo - Kolosal Server: Main server on 127.0.0.1:8080
echo - Test Suite: Automated testing of all endpoints
echo.
pause
