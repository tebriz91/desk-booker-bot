compose = docker-compose -f

dev = docker-compose.dev.yml
prod = docker-compose.yml

# Container names
app = desk-booker-bot
postgres = postgres_db
redis = redis_db

# Shell path
shell = /bin/bash

# File paths
file = /tests/test_queries.sql

#* Docker compose commands
start-dev:
	@echo Starting the development environment...
	@${compose} ${dev} up

stop-dev:
	@echo Stopping the development environment...
	@${compose} ${dev} down

# Remove all containers, networks, images, and volumes
clean-dev:
	@echo Removing all containers, networks, images, and volumes for the development environment...
	@${compose} ${dev} down -v --rmi all

start-prod:
	@echo Starting the production environment...
	@${compose} ${prod} up

stop-prod:
	@echo Stopping the production environment...
	@${compose} ${prod} down

#* Docker commands
docker-ps:
	@echo Listing all running containers for the development environment...
	@docker ps || echo Failed to list containers"

docker-network-ls:
	@echo Listing all Docker networks...
	@docker network ls || echo Failed to list Docker networks"

docker-volume-ls:
	@echo Listing all Docker volumes...
	@docker volume ls || echo Failed to list Docker volumes"

docker-prune:
	@echo Pruning all unused Docker resources...
	@docker system prune -a || echo Failed to prune Docker resources"

docker-images:	
	@echo Listing all Docker images...
	@docker images || echo Failed to list Docker images"

docker-rmi:
	@echo Removing all Docker images...
	@docker rmi $(docker images -a -q) || echo Failed to remove Docker images"

docker-rm:
	@echo Removing all Docker containers...
	@docker rm $(docker ps -a -q) || echo Failed to remove Docker containers"

docker-network-rm:
	@echo Removing all Docker networks...
	@docker network rm $(docker network ls -q) || echo Failed to remove Docker networks"

# The for loop iterates over the output of the docker volume ls -q --filter "dangling=true" command.
# Each volume ID output from the docker volume ls command is temporarily held in the %%i variable and passed to docker volume rm.
docker-volume-rm:
	@echo Removing all Docker volumes...
	@for /f "delims=" %%i in ('docker volume ls -q --filter "dangling=true"') do @docker volume rm %%i

docker-logs:
	@echo Following logs for the app container...
	@docker logs --follow ${app} || echo Failed to fetch logs for ${app}"

#* Shell commands
shell-dev:
	@echo Opening bash for the app container...
	@docker exec -it ${app} {shell} || echo Failed to open shell for ${app}"

shell-postgres:
	@echo Opening bash for the postgres container...
	@docker exec -it ${postgres} {shell} || echo Failed to open shell for ${postgres}"

shell-redis:
	@echo Opening bash for the redis container...
	@docker exec -it ${redis} {shell} || echo Failed to open shell for ${redis}"

#* Postgres commands
postgres-cli:
	@echo Opening postgres-cli...
	@docker exec -it ${postgres} psql -U postgres || echo Failed to connect to Postgres CLI"

postgres-quit:
	@echo Quitting postgres-cli...
	@docker exec -it ${postgres} psql -U postgres -c "\q" || echo Failed to quit Postgres CLI"

postgres-create-db:
	@echo Creating database...
	@docker exec -it ${postgres} createdb -U postgres ${app} || echo Failed to create database"

postgres-drop-db:
	@echo Dropping database...
	@docker exec -it ${postgres} dropdb -U postgres ${app} || echo Failed to drop database"

postgres-list-tables:
	@echo Listing all tables in the database...
	@docker exec -it ${postgres} psql -U postgres -d ${app} -c "\dt" || echo Failed to list tables in the database"

postgres-list-records:
	@echo Listing all records in the database...
	@docker exec -it ${postgres} psql -U postgres -d ${app} -c "SELECT * FROM ${table}" || echo Failed to list records in the database"

postgres-list-functions:
	@echo Listing all functions in the database...
	@docker exec -it ${postgres} psql -U postgres -d ${app} -c "\df" || echo Failed to list functions in the database"

postgres-run-query-from-file:
	@echo Running query from file...
	@docker exec -it ${postgres} psql -U postgres -d ${app} -f ${file} || echo Failed to run query from file"

postgres-backup:
	@echo Backing up the database...
	@docker exec -it ${postgres} pg_dump -U postgres ${app} > ${app}.sql || echo Failed to backup the database"

postgres-restore:
	@echo Restoring the database...
	@cat ${app}.sql | docker exec -i ${postgres} psql -U postgres ${app} || echo Failed to restore the database"

postgres-logs:
	@echo Following logs for the postgres container...
	@docker logs --follow ${postgres} || echo Failed to fetch logs for ${postgres}"

#* Redis commands
redis-cli:
	@echo Opening redis-cli...
	@docker exec -it ${redis} redis-cli || echo Failed to connect to Redis CLI"

redis-quit:
	@echo Quitting redis-cli...
	@docker exec -it ${redis} redis-cli -c "quit" || echo Failed to quit Redis CLI"

redis-flush:
	@echo Flushing redis...
	@docker exec -it ${redis} redis-cli flushall || echo Failed to flush Redis"

redis-keys:
	@echo Listing all keys in redis...
	@docker exec -it ${redis} redis-cli keys "*" || echo Failed to list Redis keys"

redis-monitor:
	@echo Monitoring redis...
	@docker exec -it ${redis} redis-cli monitor || echo Failed to monitor Redis"

#* Pytest commands
pytest:
	@echo Running tests...
	@docker exec -it ${app} pytest || echo Failed to run tests"

pytest-coverage:
	@echo Running tests with coverage...
	@docker exec -it ${app} pytest --cov=app || echo Failed to run tests with coverage"

pytest-cov-html:
	@echo Running tests with coverage and generating HTML report...
	@docker exec -it ${app} pytest --cov=app --cov-report html || echo Failed to run tests with coverage and generate HTML report"

# Running 'make test' command from root/tests/integration
pytest-integration:
	@echo Running integration tests...
	@cd tests/integration && make test || echo Failed to run integration tests"

#* Linting commands
lint:
	@echo Running linter...
	@docker exec -it ${app} flake8 || echo Failed to run linter"

lint-black:
	@echo Running Black linter...
	@docker exec -it ${app} black . || echo Failed to run Black linter"

#* Formatting commands
format:
	@echo Running Black formatter...
	@docker exec -it ${app} black . || echo Failed to run Black formatter"

#* Alembic commands
alembic-init:
	@echo Initializing Alembic...
	@docker exec -it ${app} alembic init alembic || echo Failed to initialize Alembic"

alembic-revision:
	@echo Creating a new revision...
	@docker exec -it ${app} alembic revision --autogenerate || echo Failed to create a new revision"

alembic-upgrade:
	@echo Upgrading the database...
	@docker exec -it ${app} alembic upgrade head || echo Failed to upgrade the database"

alembic-downgrade:
	@echo Downgrading the database...
	@docker exec -it ${app} alembic downgrade -1 || echo Failed to downgrade the database"

alembic-history:
	@echo Listing all Alembic revisions...
	@docker exec -it ${app} alembic history --verbose || echo Failed to list Alembic revisions"

#* UV commands
uv-install:
	@echo Installing dependencies...
	@docker exec -it ${app} uv install || echo Failed to install dependencies"

uv-update:
	@echo Updating dependencies...
	@docker exec -it ${app} uv update || echo Failed to update dependencies"

uv-show-deps:
	@echo Listing all dependencies...
	@docker exec -it ${app} uv show --tree || echo Failed to list dependencies"

#* Help command (colorized text)
help:
	@echo   Available commands
	@echo   *****************************
	@echo   Docker compose commands
	@echo     - make start-dev
	@echo     - make stop-dev
	@echo     - make clean-dev
	@echo     - make start-prod
	@echo     - make stop-prod
	@echo   *****************************
	@echo   Docker commands:
	@echo     - make docker-ps
	@echo     - make docker-network-ls
	@echo     - make docker-volume-ls
	@echo     - make docker-prune
	@echo     - make docker-images
	@echo     - make docker-rmi
	@echo     - make docker-rm
	@echo     - make docker-network-rm
	@echo     - make docker-volume-rm
	@echo     - make docker-logs
	@echo   *****************************
	@echo   Shell commands:
	@echo     - make shell-dev
	@echo     - make shell-postgres
	@echo     - make shell-redis
	@echo   *****************************
	@echo   Postgres commands:
	@echo     - make postgres-cli
	@echo     - make postgres-quit
	@echo     - make postgres-create-db
	@echo     - make postgres-drop-db
	@echo     - make postgres-list-tables
	@echo     - make postgres-list-records
	@echo     - make postgres-list-functions
	@echo     - make postgres-run-query-from-file
	@echo     - make postgres-backup
	@echo     - make postgres-restore
	@echo     - make postgres-logs
	@echo   *****************************
	@echo   Redis commands:
	@echo     - make redis-cli
	@echo     - make redis-quit
	@echo     - make redis-flush
	@echo     - make redis-keys
	@echo     - make redis-monitor
	@echo   *****************************
	@echo   Pytest commands:
	@echo     - make test
	@echo     - make test-coverage
	@echo     - make test-cov-html
	@echo   *****************************
	@echo   Linting commands:
	@echo     - make lint
	@echo     - make lint-black
	@echo   *****************************
	@echo   Formatting commands:
	@echo     - make format
	@echo   *****************************
	@echo   Alembic commands:
	@echo     - make alembic-init
	@echo     - make alembic-revision
	@echo     - make alembic-upgrade
	@echo     - make alembic-downgrade
	@echo     - make alembic-history
	@echo   *****************************
	@echo   UV commands:
	@echo     - make uv-install
	@echo     - make uv-update
	@echo     - make uv-show-deps
