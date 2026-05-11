COMPOSE_FILE := docker-compose-local.yaml
COMPOSE := docker compose -f $(COMPOSE_FILE)

up:
	docker $(COMPOSE) up -d

start: up


down:
	docker $(COMPOSE) down; docker network prune --force

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
