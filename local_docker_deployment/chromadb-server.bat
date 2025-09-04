@echo off
REM ChromaDB Server Management Script - Windows Batch Version
setlocal EnableDelayedExpansion

REM Get script directory and project root
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
cd /d "%PROJECT_ROOT%"

REM Configuration
set NETWORK_NAME=mcp-network
set COMPOSE_FILE=%SCRIPT_DIR%docker-compose.yml

if "%1"=="" (
    echo ❌ No command provided
    echo.
    goto :show_help
)

if /i "%1"=="start" goto :start_server
if /i "%1"=="stop" goto :stop_server  
if /i "%1"=="restart" goto :restart_server
if /i "%1"=="status" goto :show_status
if /i "%1"=="logs" goto :show_logs
if /i "%1"=="health" goto :check_health
if /i "%1"=="clean" goto :clean_data
if /i "%1"=="help" goto :show_help
if /i "%1"=="--help" goto :show_help
if /i "%1"=="-h" goto :show_help

echo ❌ Unknown command: %1
echo.
goto :show_help

:show_help
echo ChromaDB Server Management
echo.
echo Usage: %~nx0 [COMMAND]
echo.
echo Commands:
echo   start     Start ChromaDB server
echo   stop      Stop ChromaDB server
echo   restart   Restart ChromaDB server
echo   status    Show server status
echo   logs      Show server logs
echo   health    Check server health
echo   clean     Stop server and remove data (DANGEROUS)
echo.
goto :end

:start_server
echo 🚀 Starting ChromaDB server...

REM Create network if it doesn't exist
docker network ls | findstr "%NETWORK_NAME%" >nul
if errorlevel 1 (
    echo 🔧 Creating %NETWORK_NAME%...
    docker network create %NETWORK_NAME%
    if errorlevel 1 (
        echo ❌ Failed to create network
        exit /b 1
    )
    echo ✅ Network created
) else (
    echo ✅ Network %NETWORK_NAME% already exists
)

REM Create data directory
if not exist "data\chroma_data" mkdir data\chroma_data

REM Start ChromaDB with docker-compose
docker-compose -f "%COMPOSE_FILE%" up -d chromadb
if errorlevel 1 (
    echo ❌ Failed to start ChromaDB server
    exit /b 1
)

echo ✅ ChromaDB server started on http://localhost:8000
echo 🌐 Container name: chromadb (accessible from %NETWORK_NAME%)
echo 💡 Run '%~nx0 health' to check server status
goto :end

:stop_server
echo 🛑 Stopping ChromaDB server...
docker-compose -f "%COMPOSE_FILE%" down
echo ✅ ChromaDB server stopped
goto :end

:restart_server
echo 🔄 Restarting ChromaDB server...
call :stop_server
timeout /t 2 /nobreak >nul
call :start_server
goto :end

:show_status
echo 📊 ChromaDB server status:
docker-compose -f "%COMPOSE_FILE%" ps chromadb
goto :end

:show_logs
echo 📋 ChromaDB server logs:
docker-compose -f "%COMPOSE_FILE%" logs -f chromadb
goto :end

:check_health
echo 🏥 Checking ChromaDB server health...
curl -f http://localhost:8000/api/v2/heartbeat >nul 2>&1
if errorlevel 1 (
    echo ❌ ChromaDB server is not healthy
    echo 💡 Run '%~nx0 logs' to check for errors
    exit /b 1
) else (
    echo ✅ ChromaDB server is healthy
    echo 🌐 Server URL: http://localhost:8000
    echo 📊 Admin UI: http://localhost:8000 (if available)
    
    REM Try to get version info (if curl and basic JSON parsing available)
    echo 📦 Server info:
    curl -s http://localhost:8000/api/v2/version 2>nul || echo Version info not available
)
goto :end

:clean_data
echo ⚠️  WARNING: This will delete all ChromaDB data!
set /p confirm="Are you sure? Type 'yes' to confirm: "
if /i "%confirm%"=="yes" (
    echo 🧹 Cleaning ChromaDB data...
    call :stop_server
    if exist "data\chroma_data" (
        rmdir /s /q "data\chroma_data"
        mkdir "data\chroma_data"
    )
    echo ✅ ChromaDB data cleaned
    echo 💡 Run '%~nx0 start' to start fresh server
) else (
    echo ❌ Clean operation cancelled
)
goto :end

:end
endlocal