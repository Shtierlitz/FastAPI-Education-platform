COMPOSE_FILE := docker-compose-local.yaml
COMPOSE := docker compose -f $(COMPOSE_FILE)

up:
	$(COMPOSE) up -d

start: up


down:
	$(COMPOSE) down; docker network prune --force

run:
	docker compose -f docker-compose-ci.yaml up -d

stop: down

restart:
	$(COMPOSE) down
	$(COMPOSE) up -d

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

clean-full:
	$(COMPOSE) down --volumes --remove-orphans --rmi local
