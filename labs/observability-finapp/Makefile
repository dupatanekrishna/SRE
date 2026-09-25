.PHONY: setup up down clean status healthy slow traffic db-activity ready

setup:
	@test -f .env || cp .env.example .env
	@test -f alertmanager.yml || cp alertmanager.yml.example alertmanager.yml
	@echo "Local files ready. Edit .env and alertmanager.yml before using real Slack notifications."

up:
	docker compose up -d --build

down:
	docker compose down

clean:
	docker compose down -v

status:
	docker compose ps

healthy:
	@sed -i.bak 's/^DB_SLEEP_SECONDS=.*/DB_SLEEP_SECONDS=0/' .env && rm -f .env.bak
	docker compose up -d --build backend
	@echo "Healthy mode enabled: DB_SLEEP_SECONDS=0"

slow:
	@sed -i.bak 's/^DB_SLEEP_SECONDS=.*/DB_SLEEP_SECONDS=3/' .env && rm -f .env.bak
	docker compose up -d --build backend
	@echo "Slow DB incident enabled: DB_SLEEP_SECONDS=3"

traffic:
	bash scripts/generate-traffic.sh

db-activity:
	bash scripts/postgres-activity.sh

ready:
	@echo "Backend:" && curl -s http://localhost:8080/ && echo
	@echo "Prometheus:" && curl -s http://localhost:9090/-/ready && echo
	@echo "Alertmanager:" && curl -s http://localhost:9093/-/ready && echo
	@echo "Tempo:" && curl -s http://localhost:3200/ready && echo
