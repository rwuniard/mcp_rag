@echo off
REM MCP RAG Server Deployment Script - Windows Batch Version
REM Deploys the production Docker image from GitHub Container Registry
setlocal EnableDelayedExpansion

REM Configuration
set MCP_CONTAINER=mcp-rag-server
set GITHUB_IMAGE=ghcr.io/rwuniard/mcp_rag:latest
set NETWORK_NAME=mcp-network

REM Get script directory
set SCRIPT_DIR=%~dp0

echo 🚀 MCP RAG Server Deployment
echo ==========================================

REM Step 1: Check network exists
echo.
echo 📡 Checking Docker network...
docker network ls | findstr "%NETWORK_NAME%" >nul
if errorlevel 1 (
    echo ❌ Network '%NETWORK_NAME%' does not exist
    echo 💡 Please run ChromaDB setup first:
    echo    Use kiro-project to start ChromaDB server
    exit /b 1
)
echo ✅ Network '%NETWORK_NAME%' exists

REM Step 2: Check ChromaDB is running
echo.
echo 🗄️  Checking ChromaDB...
docker ps | findstr "chromadb" >nul
if errorlevel 1 (
    echo ❌ ChromaDB is not running
    echo 💡 Please start ChromaDB first:
    echo    Use kiro-project to start ChromaDB server
    exit /b 1
)
echo ✅ ChromaDB is running

REM Step 3: Stop existing MCP server if running
echo.
echo 🔄 Checking existing MCP RAG server...
docker-compose -f "%SCRIPT_DIR%docker-compose.mcp-server.yml" down >nul 2>&1
echo ✅ Previous MCP server stopped

REM Step 4: Pull latest production image
echo.
echo 📦 Pulling latest production Docker image...
echo Image: %GITHUB_IMAGE%
docker pull "%GITHUB_IMAGE%"
if errorlevel 1 (
    echo ❌ Failed to pull Docker image
    exit /b 1
)
echo ✅ Latest production image pulled

REM Step 5: Start MCP RAG server with docker-compose
echo.
echo 🚀 Starting MCP RAG server...
docker-compose -f "%SCRIPT_DIR%docker-compose.mcp-server.yml" up -d mcp-rag-server
if errorlevel 1 (
    echo ❌ Failed to start MCP RAG server
    exit /b 1
)

REM Step 6: Wait and verify
echo ⏳ Waiting for MCP RAG server to start...
timeout /t 8 /nobreak >nul

REM Check if container is still running
docker ps | findstr "%MCP_CONTAINER%" >nul
if errorlevel 1 (
    echo ❌ MCP RAG server failed to start
    echo 📋 Container logs:
    docker logs "%MCP_CONTAINER%"
    echo.
    echo 💡 Troubleshooting:
    echo   1. Check if ChromaDB is healthy: Use kiro-project health check
    echo   2. Check container status: docker ps -a
    echo   3. Check network: docker network ls
    exit /b 1
) else (
    echo ✅ MCP RAG server started successfully!
    
    REM Show container logs (last 10 lines)
    echo.
    echo 📋 Recent logs:
    docker logs --tail 10 "%MCP_CONTAINER%"
    
    REM Test connectivity
    echo.
    echo 🔍 Testing server connectivity...
    timeout /t 2 /nobreak >nul
    curl -f -s http://localhost:8080/health >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Health check not available (server may still be starting)
    ) else (
        echo ✅ Health check passed
    )
    
    REM Show connection info
    echo.
    echo 🎉 Deployment Complete!
    echo ==========================================
    echo MCP RAG Server: http://localhost:8080
    echo ChromaDB: http://localhost:8000
    echo Using Production API Key: ✅
    echo.
    echo 📝 Useful commands:
    echo   View logs:    docker logs -f %MCP_CONTAINER%
    echo   Stop server:  docker stop %MCP_CONTAINER%
    echo   Restart:      %~nx0
    echo   Stop ChromaDB: Use kiro-project tools
    echo.
)

endlocal