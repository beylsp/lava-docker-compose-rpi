# Host address on which LAVA is accessible.
LAVA_HOST = lmrpi.lan
# LAVA user to use.
LAVA_USER = lava
# lavacli "identity" for the above user,
# to submit jobs, etc.
LAVA_IDENTITY = lava-docker
LAVA_TOKEN = NjU3MTBjYTZhMmM3MGVmZmViZjIwMWFm

LAVA_SERVER_DOCKER_NAME = lava-server

LAVA_BOARDS_DEFINITION ?= boards.yaml

all: lava-server lava-setup lava-boards

lava-server:
	docker-compose --env-file .env up -d
	docker-compose exec $(LAVA_SERVER_DOCKER_NAME) \
		chown -R lavaserver:lavaserver /etc/lava-server/dispatcher-config/device-types
	docker-compose exec $(LAVA_SERVER_DOCKER_NAME) \
		chown -R lavaserver:lavaserver /etc/lava-server/dispatcher-config/devices

lava-setup: lava-token lava-identity lava-boards

lava-token:
	docker-compose exec $(LAVA_SERVER_DOCKER_NAME) \
		lava-server manage tokens add \
			--user $(LAVA_USER) \
			--description "lavacli token for user 'lava', to submit jobs, etc." \
			--secret $(LAVA_TOKEN)

lava-identity:
	lavacli identities add \
		--username $(LAVA_USER) \
		--token $(LAVA_TOKEN) \
		--uri http://$(LAVA_HOST)/RPC2 \
		$(LAVA_IDENTITY)
	lavacli -i $(LAVA_IDENTITY) system version

lava-boards:
	python3 board-setup-helper.py \
		--boards-definition-file $(LAVA_BOARDS_DEFINITION) \
		--lava-host $(LAVA_HOST) \
		--lava-user $(LAVA_USER) \
		--lava-token $(LAVA_TOKEN)

clean:
	docker-compose rm -vsf
	docker volume rm -f lava-server-pgdata lava-server-joboutput lava-server-device-types lava-server-devices lava-server-health-checks lava-server-worker-state lava-server-worker-http lava-server-worker-tftp

server-shell:
	docker-compose exec lava-server bash

.PHONY: all clean
