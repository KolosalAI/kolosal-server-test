@echo off
setlocal enabledelayedexpansion

REM Load .env variables
for /f "tokens=1,* delims==" %%a in ('type ".env"') do (
    set "%%a=%%b"
)


REM Start Qdrant in Docker
start "Qdrant" powershell -NoExit -Command ^
"cd '!QDRANT_SERVER_PATH!'; docker run -p !QDRANT_PORT_1!:!QDRANT_PORT_1! -p !QDRANT_PORT_2!:!QDRANT_PORT_2! -v '!QDRANT_VOLUME_PATH!:/qdrant/storage' qdrant/qdrant; Start-Sleep -Seconds 3"


REM Run kolosal-server.exe
start "Kolosal Server" powershell -NoExit -Command ^
"cd '!KOLOSAL_SERVER_PATH!'; .\!KOLOSAL_EXE_PATH!; Start-Sleep -Seconds 3"

REM Run test script with virtual environment
start "Kolosal Test" powershell -NoExit -Command ^
"cd '!TEST_SERVER_PATH!'; .\!VENV_ACTIVATE_PATH!; !TEST_RUN_COMMAND!; uv run python main.py"
