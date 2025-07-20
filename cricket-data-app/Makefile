# Cricket App Docker Management

.PHONY: help build up down restart logs clean test dev prod setup

# Default target
help:
	@echo "Cricket App Docker Management"
	@echo "============================="
	@echo ""
	@echo "Available commands:"
	@echo "  setup    - Setup the project for Docker"
	@echo "  build    - Build all Docker images"
	@echo "  up       - Start all services"
	@echo "  down     - Stop all services"
	@echo "  restart  - Restart all services"
	@echo "  logs     - Show logs from all services"
	@echo "  clean    - Remove all containers, images and volumes"
	@echo "  test     - Run tests in Docker containers"
	@echo "  dev      - Start in development mode with live reload"
	@echo "  prod     - Start in production mode"
	@echo ""

# Setup project for Docker
setup:
	@echo "Setting up Docker configuration..."
	@cp nginx.conf frontend/nginx.conf
	@echo "# Backend .dockerignore" > backend/.dockerignore
	@echo "**/__pycache__" >> backend/.dockerignore
	@echo "**/*.pyc" >> backend/.dockerignore
	@echo "**/venv/" >> backend/.dockerignore
	@echo "**/tests/" >> backend/.dockerignore
	@echo "**/.pytest_cache/" >> backend/.dockerignore
	@echo "**/.coverage" >> backend/.dockerignore
	@echo "# Frontend .dockerignore" > frontend/.dockerignore
	@echo "**/node_modules" >> frontend/.dockerignore
	@echo "**/build" >> frontend/.dockerignore
	@echo "**/coverage" >> frontend/.dockerignore
	@echo "**/npm-debug.log*" >> frontend/.dockerignore
	@echo "Setup complete!"

# Build all images
build:
	@echo "Building Docker images..."
	docker-compose build --no-cache

# Start all services
up:
	@echo "Starting all services..."
	docker-compose up -d
	@echo "Services started. Access the app at http://localhost"
	@echo "Backend API available at http://localhost:8000"

# Stop all services
down:
	@echo "Stopping all services..."
	docker-compose down

# Restart all services
restart: down up

# Show logs
logs:
	docker-compose logs -f

# Show logs for specific service
logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

# Clean up everything
clean:
	@echo "Cleaning up Docker resources..."
	docker-compose down -v --rmi all --remove-orphans
	docker system prune -af
	@echo "Cleanup complete!"

# Run tests
test:
	@echo "Running backend tests..."
	docker-compose exec backend pytest -v
	@echo "Running frontend tests..."
	docker-compose exec frontend npm test -- --coverage --watchAll=false

# Development mode with live reload
dev:
	@echo "Starting in development mode..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production mode
prod: build up

# Check service status
status:
	docker-compose ps

# Shell access to services
shell-backend:
	docker-compose exec backend /bin/bash

shell-frontend:
	docker-compose exec frontend /bin/sh

# View container resource usage
stats:
	docker stats cricket-backend cricket-frontend

# Backup database
backup:
	@echo "Creating database backup..."
	docker-compose exec backend cp /app/cricket_data.db /app/data/backup_$(shell date +%Y%m%d_%H%M%S).db
	@echo "Backup created in backend/data/ directory"

# Initialize database with fresh data
init-db:
	@echo "Initializing database..."
	docker-compose exec backend python -c "from app.services.data_loader import DataLoaderService; DataLoaderService().load_all_data()"
	@echo "Database initialized!"
