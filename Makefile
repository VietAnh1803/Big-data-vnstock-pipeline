# Vietnam Stock Pipeline - Makefile
# Simplified and optimized for production use

.PHONY: help up down restart status logs clean

# Default target
help: ## Show this help message
	@echo "📈 Vietnam Stock Pipeline - Available Commands:"
	@echo "=============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# System Management
up: ## Start all services
	@echo "🚀 Starting Vietnam Stock Pipeline..."
	docker compose up -d
	@echo "✅ System started! Dashboard: http://localhost:8501"

down: ## Stop all services
	@echo "🛑 Stopping Vietnam Stock Pipeline..."
	docker compose down
	@echo "✅ System stopped!"

restart: ## Restart all services
	@echo "🔄 Restarting Vietnam Stock Pipeline..."
	docker compose restart
	@echo "✅ System restarted!"

status: ## Check system status
	@echo "📊 System Status:"
	@docker compose ps

logs: ## Show system logs
	@echo "📋 System Logs:"
	@docker compose logs --tail=50

clean: ## Clean up containers and images
	@echo "🧹 Cleaning up..."
	docker compose down --volumes --remove-orphans
	docker system prune -f
	@echo "✅ Cleanup completed!"

# Data Operations
fetch-comprehensive: ## Fetch comprehensive data from vnstock
	@echo "🚀 Fetching comprehensive data from vnstock..."
	@echo "📊 This includes: company profiles, financial reports, market data..."
	@echo "⚠️  This will take a long time (1000+ tickers)..."
	docker compose --profile comprehensive up --build comprehensive-producer


fetch-historical-2017: ## Fetch historical data from 2017
	@echo "🚀 Fetching historical data from 2017..."
	@echo "⚠️  This will take a very long time (8+ years of data)..."
	docker compose --profile historical-2017 up --build historical-2017-fetcher

# Dashboard

# Development
dev: ## Start development environment
	@echo "🛠️ Starting development environment..."
	docker compose up -d postgres kafka zookeeper
	@echo "✅ Development services started!"

# Production
prod: ## Start production environment
	@echo "🏭 Starting production environment..."
	docker compose up -d
	@echo "✅ Production environment started!"

# Monitoring
monitor: ## Monitor system health
	@echo "📊 System Health Monitor:"
	@echo "========================"
	@docker compose ps
	@echo ""
	@echo "📈 Dashboard Status:"
	@curl -s -o /dev/null -w "Dashboard: %{http_code}\n" http://localhost:8501 || echo "Dashboard: Not accessible"
	@curl -s -o /dev/null -w "Real-time: %{http_code}\n" http://localhost:8502 || echo "Real-time: Not accessible"


sync-data: ## Sync PostgreSQL data to Snowflake
	@echo "🔄 Starting PostgreSQL to Snowflake data synchronization..."
	@echo "📊 This will sync all tables and remove empty ones in Snowflake..."
	@echo "⚠️  This may take a while depending on data size..."
	docker compose --profile sync up --build data-sync

logs-sync: ## Show sync logs
	@echo "📋 Data Sync Logs:"
	@docker compose --profile sync logs -f data-sync


# Backup
backup: ## Backup database
	@echo "💾 Creating database backup..."
	@mkdir -p backups
	docker compose exec postgres pg_dump -U admin stock_db > backups/stock_db_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created in backups/ directory"

# Restore
restore: ## Restore database from backup
	@echo "🔄 Restoring database from backup..."
	@echo "⚠️  This will overwrite existing data!"
	@read -p "Enter backup filename: " backup_file; \
	docker compose exec -T postgres psql -U admin stock_db < backups/$$backup_file
	@echo "✅ Database restored!"

# Quick Commands
quick-start: up ## Quick start (alias for up)
	@echo "🎯 Quick start completed!"

quick-stop: down ## Quick stop (alias for down)
	@echo "🛑 Quick stop completed!"

# Health Check
health: ## Check system health
	@echo "🏥 System Health Check:"
	@echo "======================"
	@docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "🔍 Service Health:"
	@docker compose exec postgres pg_isready -U admin || echo "❌ PostgreSQL: Not ready"
	@docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list > /dev/null 2>&1 && echo "✅ Kafka: Ready" || echo "❌ Kafka: Not ready"