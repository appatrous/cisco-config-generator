#!/bin/bash
# Development startup script

echo "🚀 Starting Cisco Config Generator - Development Mode"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env created. Please review and update if needed."
    echo ""
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "🐳 Starting Docker containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if database needs initialization
echo "🔍 Checking if database is initialized..."
if docker-compose exec -T api python -c "from app_api import create_app; from extensions import db; app = create_app(); app.app_context().push(); print('Tables:', len(db.metadata.tables))" 2>/dev/null | grep -q "Tables: 0"; then
    echo "📊 Initializing database..."
    docker-compose exec -T api python init_db.py
else
    echo "✅ Database already initialized"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All services are running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📡 Services:"
echo "   • API:        http://localhost:5000"
echo "   • PostgreSQL: localhost:5432"
echo "   • Redis:      localhost:6379"
echo ""
echo "🔑 Default Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo "   ⚠️  Change this in production!"
echo ""
echo "📋 Useful Commands:"
echo "   • View logs:        docker-compose logs -f"
echo "   • Stop services:    docker-compose down"
echo "   • Restart:          docker-compose restart"
echo "   • View status:      docker-compose ps"
echo ""
echo "🧪 Test the API:"
echo "   curl http://localhost:5000/api/health"
echo ""

# Optionally open browser
if command -v xdg-open > /dev/null; then
    read -p "Open browser? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        xdg-open http://localhost:5000/api/health
    fi
fi
