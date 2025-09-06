@echo off
REM Local Docker Deployment Script for Windows (Build from Local Source)

setlocal enabledelayedexpansion

echo [INFO] Starting local Docker deployment (building from local source)...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Set build metadata
for /f "delims=" %%i in ('powershell -command "Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ'"') do set BUILD_DATE=%%i
for /f "delims=" %%i in ('git rev-parse --short HEAD 2^>nul ^|^| echo unknown') do set GIT_COMMIT=%%i
for /f "delims=" %%i in ('git rev-parse --abbrev-ref HEAD 2^>nul ^|^| echo unknown') do set GIT_BRANCH=%%i
for /f "delims=" %%i in ('git describe --tags --always 2^>nul ^|^| echo dev') do set VERSION=%%i

echo [INFO] Build metadata:
echo [INFO]   Build Date: !BUILD_DATE!
echo [INFO]   Git Commit: !GIT_COMMIT!
echo [INFO]   Git Branch: !GIT_BRANCH!
echo [INFO]   Version: !VERSION!

REM Create network if it doesn't exist
echo [INFO] Creating Docker network 'mcp-network' if it doesn't exist...
docker network create mcp-network 2>nul || echo [WARNING] Network 'mcp-network' already exists

REM Create data directory
echo [INFO] Creating data directory...
if not exist "data\chroma_data" mkdir data\chroma_data

REM Stop any existing containers
echo [INFO] Stopping existing containers...
docker-compose -f docker-compose.yml down 2>nul
docker-compose -f docker-compose.mcp-server.yml down 2>nul

REM Start ChromaDB first
echo [INFO] Starting ChromaDB...
docker-compose -f docker-compose.yml up -d chromadb

REM Wait for ChromaDB to be ready
echo [INFO] Waiting for ChromaDB to be ready...
set /a timeout=60
set /a counter=0
:wait_chromadb
docker exec chromadb curl -f http://localhost:8000/api/v1/heartbeat >nul 2>&1
if not errorlevel 1 goto chromadb_ready
if !counter! geq !timeout! (
    echo [ERROR] ChromaDB failed to start within !timeout! seconds
    docker-compose -f docker-compose.yml logs chromadb
    exit /b 1
)
echo|set /p="."
timeout /t 1 /nobreak >nul
set /a counter+=1
goto wait_chromadb

:chromadb_ready
echo.
echo [SUCCESS] ChromaDB is ready!

REM Build and start MCP RAG Server
echo [INFO] Building and starting MCP RAG Server (this may take a few minutes)...
docker-compose -f docker-compose.mcp-server.yml up -d --build

REM Wait for MCP RAG Server to be ready
echo [INFO] Waiting for MCP RAG Server to be ready...
set /a timeout=120
set /a counter=0
:wait_mcp_server
docker exec mcp-rag-server-local curl -f http://localhost:8080/health >nul 2>&1
if not errorlevel 1 goto mcp_server_ready
if !counter! geq !timeout! (
    echo [ERROR] MCP RAG Server failed to start within !timeout! seconds
    docker-compose -f docker-compose.mcp-server.yml logs mcp-rag-server
    exit /b 1
)
echo|set /p="."
timeout /t 1 /nobreak >nul
set /a counter+=1
goto wait_mcp_server

:mcp_server_ready
echo.
echo [SUCCESS] All services are running!
echo [INFO] Services available at:
echo [INFO]   ChromaDB: http://localhost:8000
echo [INFO]   MCP RAG Server: http://localhost:8080
echo [INFO]   Health Check: http://localhost:8080/health

echo [INFO] To view logs, run:
echo [INFO]   docker-compose -f docker-compose.yml logs -f chromadb
echo [INFO]   docker-compose -f docker-compose.mcp-server.yml logs -f mcp-rag-server

echo [INFO] To stop services, run:
echo [INFO]   shutdown.bat