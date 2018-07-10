.PHONY: build-docs clean load-fixtures help build no-deps
.DEFAULT_GOAL := help

# Variables ---------------------------------------------------------------------------------------
SELF := $(abspath $(lastword $(MAKEFILE_LIST)))
PWD := $(patsubst %/,%,$(dir $(SELF)))
CWD := /opt/services/djangoapp/src

DOCKER := docker
DOCKER_COMPOSE := docker-compose
COMPOSE_FILE := docker-compose.yml

#ifdef GITLAB_CI
#  DJANGO_SETTINGS_MODULE := logan.settings.ci
#else
  ifndef HOSTNAME
    HOSTNAME := $(shell hostname)
  endif
#  ifeq ($(HOSTNAME), logan)
#    DJANGO_SETTINGS_MODULE := logan.settings.prod
#    COMPOSE_FILE := compose-production.yml
#  else ifeq ($(HOSTNAME), logan-staging)
#    DJANGO_SETTINGS_MODULE := logan.settings.staging
#    COMPOSE_FILE := compose-staging.yml
#  else
#    DJANGO_SETTINGS_MODULE := logan.settings.local
#    COMPOSE_FILE := compose-development.yml
#  endif
#endif
DJANGO_SETTINGS_MODULE := logan.settings

DOCKER_COMPOSE += -f docker/$(COMPOSE_FILE) --project-directory .

RUN_DJANGOAPP = $(DOCKER_COMPOSE) run $(RUN_OPTS) --rm djangoapp
MAKE_IN = $(RUN_DJANGOAPP) make -f Makefile.in-container

DOCKER0_ADDRESS := $(shell ifconfig | grep docker0 -A 1 | grep -Eo 'inet add?r:[^ ]*' | cut -d: -f2)

export DJANGO_SETTINGS_MODULE
export DOCKER0_ADDRESS

# Information -------------------------------------------------------------------------------------
$(info ----------------------------------------------------)
$(info HOSTNAME                = $(HOSTNAME))
$(info COMPOSE_FILE            = $(COMPOSE_FILE))
$(info DOCKER0_ADDRESS         = $(DOCKER0_ADDRESS))
$(info DJANGO_SETTINGS_MODULE  = $(DJANGO_SETTINGS_MODULE))
$(info ----------------------------------------------------)
$(info )

# Building rules ----------------------------------------------------------------------------------
all: build up-no-start build-database load-fixtures build-superuser up ## Build images, create tables, insert fixtures, create super user and start application.

build: ## Build the Docker images.
	$(DOCKER_COMPOSE) build

build-django: ## Build the image for Django.
	$(DOCKER_COMPOSE) build djangoapp

build-database: ## Migrate the application database (create or alter tables).
	@$(MAKE_IN) build-database

build-initial-migrations: no-deps ## Create the initial database migrations.
	@$(MAKE_IN) build-initial-migrations

build-superuser: ## Create a super user in the application database.
	@$(MAKE_IN) build-superuser

build-docs: ## Build the documentation.
	@$(MAKE_IN) build-docs

# Running rules -----------------------------------------------------------------------------------
up: ## Start the application.
	$(DOCKER_COMPOSE) up

up-no-start: ## Create the containers without starting the application.
	$(DOCKER_COMPOSE) up --no-start

up-daemon: ## Start the application in background.
	$(DOCKER_COMPOSE) up -d

down: ## Stop the application.
	$(DOCKER_COMPOSE) down

shell: ## Launch a shell in the djangoapp container.
	@$(RUN_DJANGOAPP) bash

python: ## Launch a Python shell in the djangoapp container.
	@$(MAKE_IN) python

# Updating rules ----------------------------------------------------------------------------------
load-static-files: delete-django-image delete-static-volume build-django ## Collect static files.

load-fixtures: ## Install the fixtures in the database.
	@$(MAKE_IN) load-fixtures

load-warehouse: ## Reload the questionnaires answers into the analysis tables.
	@$(MAKE_IN) load-warehouse

update-migrations: ## Update the database migrations.
	@$(MAKE_IN) update-migrations

create-data-migration: ## Create a new, empty data migration for app APP.
	@$(MAKE_IN) create-data-migration APP=$(APP)

reset-migrations: delete-migrations build-initial-migrations ## Delete all migrations and re-create the initial migrations.

# Backup rules ------------------------------------------------------------------------------------
backup-databases: ## Backup the databases.
	@$(MAKE_IN) backup-databases

# Testing / Linting rules -------------------------------------------------------------------------
check: check-safety check-bandit check-pylint check-isort check-docs-links check-docs-spelling ## Run all the check jobs.

test: up-daemon pytest down ## Run the test jobs within the whole container infrastructure.

pytest: ## Run the test suite.
	@$(MAKE_IN) pytest

no-deps:
	$(eval RUN_OPTS = --no-deps)

check-safety: no-deps ## Run safety on the dependencies.
	@$(MAKE_IN) check-safety

check-bandit: no-deps ## Run bandit on the code.
	@$(MAKE_IN) check-bandit

check-pylint: no-deps ## Run pylint on the code.
	@$(MAKE_IN) check-pylint

isort: no-deps ## Run isort (write files) on the code.
	@$(MAKE_IN) isort

check-isort: no-deps ## Run isort check on the code.
	@$(MAKE_IN) check-isort

check-docs-links: no-deps ## Check the documentation (spelling, URLs).
	@$(MAKE_IN) check-docs-links

check-docs-spelling: no-deps ## Check the documentation (spelling, URLs).
	@$(MAKE_IN) check-docs-spelling

# Cleaning rules ----------------------------------------------------------------------------------
delete-database-volumes: down ## Delete the database volumes. Don't do this in production!!
	$(DOCKER) volume rm -f data

delete-django-image: down ## Delete the Docker image for the djangoapp service.
	$(DOCKER) image rm logan_djangoapp || true

delete-static-volume: down ## Delete the Docker volume storing static assets.
	$(DOCKER) volume rm logan_static || true

delete-migrations: no-deps ## Delete the migrations.
	@$(MAKE_IN) delete-migrations

clean: ## Remove artifacts (build/docs dirs, coverage files, etc.)
	rm -rf build/* 2>/dev/null
	rm -rf .cache 2>/dev/null
	rm -rf .pytest_cache 2>/dev/null
	find . -type f -name "*.pyc" -delete 2>/dev/null
	find . -type d -name __pycache__ -delete 2>/dev/null

clean-docker: down ## Stop and remove containers, volumes and networks.
	$(DOCKER) system prune -f || true

# Monitoring rules --------------------------------------------------------------------------------
goaccess: ## Run goaccess web interface to monitor NginX logs.
	@mkdir nginx-report 2>/dev/null || true
	@$(DOCKER) logs -f logan_nginx_1 2>/dev/null | \
	  goaccess --log-format=COMBINED -o nginx-report/index.html --real-time-html - &
	@xdg-open nginx-report/index.html >/dev/null 2>/dev/null &

goaccess-syslog: ## Run goaccess web interface to monitor NginX logs.
	@mkdir nginx-report 2>/dev/null || true
	@sudo tail -n+1 -f /var/log/syslog | \
	  grep 'logan-nginx' | \
	  sed 's/^.*logan-nginx\[[0-9]*\]: //' | \
	  goaccess --log-format=COMBINED -o nginx-report/index.html --real-time-html - &
	@xdg-open nginx-report/index.html >/dev/null 2>/dev/null &

# Usage rules -------------------------------------------------------------------------------------
help: ## Print this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort
