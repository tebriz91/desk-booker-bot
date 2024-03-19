compose = docker-compose -f

dev = docker-compose.dev.yml
prod = docker-compose.yml


build-dev:
	${compose} ${dev} build

start-dev:
	${compose} ${dev} up

stop-dev:
	${compose} ${dev} down

build-prod:
	${compose} ${prod} build

start-prod:
	${compose} ${prod} up

stop-prod:
	${compose} ${prod} down