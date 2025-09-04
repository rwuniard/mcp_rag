#!/bin/bash
# ChromaDB Server Management Script

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SETUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

show_help() {
    echo "ChromaDB Server Management"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start ChromaDB server"
    echo "  stop      Stop ChromaDB server"  
    echo "  restart   Restart ChromaDB server"
    echo "  status    Show server status"
    echo "  logs      Show server logs"
    echo "  health    Check server health"
    echo "  clean     Stop server and remove data (DANGEROUS)"
    echo ""
}

start_server() {
    echo "🚀 Starting ChromaDB server..."
    
    # Create network if it doesn't exist
    if ! docker network ls | grep -q "mcp-network"; then
        echo "🔧 Creating mcp-network..."
        docker network create mcp-network
        echo "✅ Network created"
    else
        echo "✅ Network mcp-network already exists"
    fi
    
    # Create data directory
    mkdir -p data/chroma_data
    
    # Start ChromaDB with docker-compose
    docker-compose -f "$SETUP_DIR/docker-compose.yml" up -d chromadb
    
    echo "✅ ChromaDB server started on http://localhost:8000"
    echo "🌐 Container name: chromadb (accessible from mcp-network)"
    echo "💡 Run '$0 health' to check server status"
}

stop_server() {
    echo "🛑 Stopping ChromaDB server..."
    docker-compose -f "$SETUP_DIR/docker-compose.yml" down
    echo "✅ ChromaDB server stopped"
}

restart_server() {
    echo "🔄 Restarting ChromaDB server..."
    stop_server
    sleep 2
    start_server
}

show_status() {
    echo "📊 ChromaDB server status:"
    docker-compose -f "$SETUP_DIR/docker-compose.yml" ps chromadb
}

show_logs() {
    echo "📋 ChromaDB server logs:"
    docker-compose -f "$SETUP_DIR/docker-compose.yml" logs -f chromadb
}

check_health() {
    echo "🏥 Checking ChromaDB server health..."
    if curl -f http://localhost:8000/api/v2/heartbeat >/dev/null 2>&1; then
        echo "✅ ChromaDB server is healthy"
        echo "🌐 Server URL: http://localhost:8000"
        echo "📊 Admin UI: http://localhost:8000 (if available)"
        
        # Try to get version info
        if command -v jq >/dev/null 2>&1; then
            echo "📦 Server info:"
            curl -s http://localhost:8000/api/v2/version | jq '.' 2>/dev/null || echo "Version info not available"
        fi
    else
        echo "❌ ChromaDB server is not healthy"
        echo "💡 Run '$0 logs' to check for errors"
        exit 1
    fi
}

clean_data() {
    echo "⚠️  WARNING: This will delete all ChromaDB data!"
    read -p "Are you sure? Type 'yes' to confirm: " confirm
    if [ "$confirm" = "yes" ]; then
        echo "🧹 Cleaning ChromaDB data..."
        stop_server
        rm -rf data/chroma_data/*
        echo "✅ ChromaDB data cleaned"
        echo "💡 Run '$0 start' to start fresh server"
    else
        echo "❌ Clean operation cancelled"
    fi
}

# Main command processing
case "${1:-}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    health)
        check_health
        ;;
    clean)
        clean_data
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        echo "❌ No command provided"
        echo ""
        show_help
        exit 1
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac