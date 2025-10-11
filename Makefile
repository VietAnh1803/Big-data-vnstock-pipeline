.PHONY: help build up down restart logs clean status check-requirements \
        prod-setup prod-setup-snowflake prod-status prod-start prod-stop \
        prod-restart prod-logs prod-uninstall monitor backup \
        fetch-data sync-snowflake big-data-setup

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development Commands
check-requirements: ## Check all system requirements
	@./scripts/check-requirements.sh

build: ## Build all Docker images
	docker-compose build

up: ## Start all services (development)
	docker-compose up -d

up-snowflake: ## Start all services with Snowflake sync
	docker-compose --profile snowflake up -d

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## View logs from all services
	docker-compose logs -f

status: ## Show status of all services
	@bash scripts/check_status.sh

clean: ## Stop and remove all containers, networks, and volumes
	docker-compose down -v
	docker system prune -f

# Production Commands
prod-setup: ## Setup production (systemd + cron + monitoring)
	@echo "Setting up production environment..."
	@chmod +x setup_production.sh
	sudo ./setup_production.sh

prod-setup-snowflake: ## Setup production with Snowflake sync
	@echo "Setting up production with Snowflake..."
	@chmod +x setup_production.sh
	sudo ./setup_production.sh --snowflake

prod-status: ## Check production status
	@bash scripts/check_status.sh

prod-start: ## Start production services
	@bash scripts/start_all.sh

prod-stop: ## Stop production services
	@bash scripts/stop_all.sh

prod-restart: ## Restart production services
	sudo systemctl restart vietnam-stock-pipeline || sudo systemctl restart vietnam-stock-pipeline-with-snowflake

prod-logs: ## View production logs
	sudo journalctl -u vietnam-stock-pipeline -f || sudo journalctl -u vietnam-stock-pipeline-with-snowflake -f

prod-uninstall: ## Uninstall production setup
	@bash scripts/uninstall_production.sh

monitor: ## Run health monitoring
	@bash scripts/monitor_services.sh

healthcheck: ## Quick health check
	@bash scripts/healthcheck.sh

# Service Logs
producer-logs: ## View producer logs
	docker-compose logs -f producer

consumer-logs: ## View consumer logs
	docker-compose logs -f consumer

spark-logs: ## View spark processor logs
	docker-compose logs -f spark-processor

dashboard-logs: ## View dashboard logs
	docker-compose logs -f dashboard

snowflake-logs: ## View Snowflake sync logs
	docker-compose logs -f snowflake-sync

# Kafka Commands
kafka-topics: ## List all Kafka topics
	docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list

kafka-consume: ## Consume messages from Kafka topic
	docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic stock-quotes --from-beginning --max-messages 10

# Database Commands
postgres-shell: ## Open PostgreSQL shell
	docker exec -it postgres psql -U admin -d stock_db

postgres-count: ## Count records in PostgreSQL
	docker exec postgres psql -U admin -d stock_db -c "SELECT COUNT(*) FROM realtime_quotes;"

postgres-stats: ## Show database statistics
	docker exec postgres psql -U admin -d stock_db -c "\
		SELECT \
			COUNT(*) as total_records, \
			COUNT(DISTINCT ticker) as unique_tickers, \
			MIN(time) as earliest_date, \
			MAX(time) as latest_date \
		FROM realtime_quotes;"

postgres-tickers: ## Show top 10 tickers by record count
	docker exec postgres psql -U admin -d stock_db -c "\
		SELECT ticker, COUNT(*) as records \
		FROM realtime_quotes \
		GROUP BY ticker \
		ORDER BY records DESC \
		LIMIT 10;"

# Backup Commands
backup: ## Backup PostgreSQL database
	@mkdir -p backups
	docker exec postgres pg_dump -U admin stock_db | gzip > backups/stock_db_$$(date +%Y%m%d_%H%M%S).sql.gz
	@echo "Backup created: backups/stock_db_$$(date +%Y%m%d_%H%M%S).sql.gz"

backup-volumes: ## Backup Docker volumes
	@mkdir -p backups
	docker run --rm -v vietnam-stock-pipeline_postgres-data:/data -v $$(pwd)/backups:/backup alpine tar czf /backup/postgres-data-$$(date +%Y%m%d).tar.gz -C /data .
	@echo "Volume backup created: backups/postgres-data-$$(date +%Y%m%d).tar.gz"

# UI Commands
spark-ui: ## Open Spark Master UI in browser
	@echo "Opening Spark Master UI at http://localhost:8080"
	@which xdg-open > /dev/null && xdg-open http://localhost:8080 || open http://localhost:8080 || echo "Please open http://localhost:8080 in your browser"

dashboard-ui: ## Open Dashboard in browser
	@echo "Opening Dashboard at http://localhost:8501"
	@which xdg-open > /dev/null && xdg-open http://localhost:8501 || open http://localhost:8501 || echo "Please open http://localhost:8501 in your browser"

pgadmin-ui: ## Open pgAdmin in browser
	@echo "Opening pgAdmin at http://localhost:5050"
	@which xdg-open > /dev/null && xdg-open http://localhost:5050 || open http://localhost:5050 || echo "Please open http://localhost:5050 in your browser"

# BIG DATA Commands
fetch-data: ## Fetch ALL data from vnstock (ticker info, financials, historical prices)
	@echo "🚀 Fetching ALL data from vnstock..."
	@echo "⚠️  This will take a while (1000+ tickers)..."
	docker compose --profile data-fetch up --build data-fetcher

fetch-complete-data: ## Fetch COMPLETE data (profiles, indicators, analytics, indices)
	@echo "🚀 Fetching COMPLETE data from vnstock..."
	@echo "⚠️  This includes profiles, indicators, analytics, and indices..."
	docker compose --profile complete-data up --build complete-data-fetcher

fetch-historical-2017: ## Fetch historical data from 2017 to present
	@echo "🚀 Fetching historical data from 2017..."
	@echo "⚠️  This will take a very long time (8+ years of data)..."
	docker compose --profile historical-2017 up --build historical-2017-fetcher

sync-snowflake: ## Sync all tables to Snowflake
	@echo "🚀 Syncing all tables to Snowflake..."
	docker run --rm \
		--network vietnam-stock-pipeline_stock-network \
		-e POSTGRES_HOST=postgres \
		-e POSTGRES_PORT=5432 \
		-e POSTGRES_DB=$${POSTGRES_DB:-stock_db} \
		-e POSTGRES_USER=$${POSTGRES_USER:-admin} \
		-e POSTGRES_PASSWORD=$${POSTGRES_PASSWORD:-admin} \
		-e SNOWFLAKE_ACCOUNT=$${SNOWFLAKE_ACCOUNT} \
		-e SNOWFLAKE_USER=$${SNOWFLAKE_USER} \
		-e SNOWFLAKE_PASSWORD=$${SNOWFLAKE_PASSWORD} \
		-e SNOWFLAKE_WAREHOUSE=$${SNOWFLAKE_WAREHOUSE:-COMPUTE_WH} \
		-e SNOWFLAKE_DATABASE=$${SNOWFLAKE_DATABASE:-STOCKS} \
		-e SNOWFLAKE_SCHEMA=$${SNOWFLAKE_SCHEMA:-PUBLIC} \
		-e SNOWFLAKE_ROLE=$${SNOWFLAKE_ROLE:-ACCOUNTADMIN} \
		-v $$(pwd)/scripts:/app \
		python:3.10-slim \
		bash -c "pip install -q snowflake-connector-python psycopg2-binary python-dotenv && python /app/sync_all_to_snowflake.py"

big-data-setup: ## Complete BIG DATA setup (fetch data + sync to Snowflake)
	@echo "🚀 BIG DATA PIPELINE SETUP"
	@echo "=========================="
	@echo ""
	@echo "Step 1: Fetching all data from vnstock..."
	@$(MAKE) fetch-data
	@echo ""
	@echo "Step 2: Syncing to Snowflake..."
	@$(MAKE) sync-snowflake
	@echo ""
	@echo "✅ BIG DATA setup completed!"

# Database queries
ticker-count: ## Count tickers in database
	@docker exec postgres psql -U admin -d stock_db -c "SELECT exchange, COUNT(*) FROM ticker_info GROUP BY exchange ORDER BY exchange;"

data-stats: ## Show data statistics
	@echo "📊 DATABASE STATISTICS"
	@echo "===================="
	@docker exec postgres psql -U admin -d stock_db -c "\
		SELECT 'ticker_info' as table_name, COUNT(*) as rows FROM ticker_info \
		UNION ALL SELECT 'historical_prices', COUNT(*) FROM historical_prices \
		UNION ALL SELECT 'realtime_quotes', COUNT(*) FROM realtime_quotes \
		UNION ALL SELECT 'stock_analytics', COUNT(*) FROM stock_analytics;"

