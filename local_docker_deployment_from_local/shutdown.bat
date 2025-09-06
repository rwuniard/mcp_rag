@echo off
REM Local Docker Shutdown Script for Windows (Local Build Version)

echo [INFO] Stopping local Docker deployment (local build)...

REM Stop MCP RAG Server
echo [INFO] Stopping MCP RAG Server...
docker-compose -f docker-compose.mcp-server.yml down 2>nul || echo [WARNING] MCP RAG Server was not running

REM Stop ChromaDB
echo [INFO] Stopping ChromaDB...
docker-compose -f docker-compose.yml down 2>nul || echo [WARNING] ChromaDB was not running

echo [SUCCESS] All services stopped!
echo [INFO] Data is preserved in .\data\chroma_data
echo [INFO] To restart, run: deploy.bat