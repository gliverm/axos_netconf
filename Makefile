.DEFAULT_GOAL := help

MODULE := st-scale-toolbox
export PWD=
BLUE='\033[0;34m'
NC='\033[0m' # No Color

#help:  @ List available tasks on this project
help:
	@grep -E '[0-9a-zA-Z\.\-]+:.*?@ .*$$' $(MAKEFILE_LIST)| sort | tr -d '#'  | awk 'BEGIN {FS = ":.*?@ "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

#dev.builddev:  @ Build docker image for development environment
dev.builddev:
	@echo "\n${BLUE}Building Docker image for app development ...${NC}\n"
	docker build --file Dockerfile --target dev -t st-scale-toolbox-dev:test .

#dev.vsc:  @ Display example docker command to start container if using Visual Studio Code
dev.vsc:
	@echo "\n${BLUE}Example of starting dev container for development...${NC}"
	@echo "\n   docker container run -it -d -v ~/OneDrive\ -\ Calix,\ Inc/BitBucket/st-scale-toolbox:/development  --name st-scale-toolbox-dev st-scale-toolbox-dev:test \n"

#dev.bandit: @ Runs static python security linter bandit - intended to be executed when developing inside container
dev.bandit:
	@echo "\n${BLUE}Run bandit ...${NC}\n"
	bandit -r --ini setup.cfg

#dev.pylint: @ Runs static python linter pylint - intended to be executed when developing inside container
dev.pylint:
	@echo "\n${BLUE}Run pylint ...${NC}\n"
	pylint --fail-under=8.0 --rcfile=setup.cfg app

#dev.flake8: @ Runs static python linter flake8 - intended to be executed when developing inside container
dev.flake8:
	@echo "\n${BLUE}Run flake8 ...${NC}\n"
	flake8 --config=setup.cfg app/

#dev.hadolint: @ Runs static docker linter hadolint - cannot be executed inside container
dev.hadolint:
	@echo "\n${BLUE}Run hadolint ...${NC}\n"
	docker container run --rm -i hadolint/hadolint hadolint - < Dockerfile

#dev.buildlinter:  @ Build docker image for linting
dev.buildlinter:
	@echo "\n${BLUE}Building Docker image for code linting ...${NC}\n"
	docker build --file Dockerfile --target qa -t st-scale-toolbox-qa:test .

#dev.dockerlint:  @ Runs linting in dev docker image
dev.dockerlint:
	@echo "\n${BLUE}Run pylint ...${NC}\n"
	docker run -i --rm -v $$(pwd):/code -w /code st-scale-toolbox-qa:test pylint --exit-zero --rcfile=setup.cfg app
	@echo "\n${BLUE}Run flake8 ...${NC}\n"
	docker run -i --rm -v $$(pwd):/code -w /code st-scale-toolbox-qa:test flake8 --exit-zero app
	@echo "\n${BLUE}Run bandit ...${NC}\n"
	docker run -i --rm -v $$(pwd):/code -w /code st-scale-toolbox-qa:test bandit -r --ini setup.cfg || true
	@echo "\n${BLUE}Run black format checker ...${NC}\n"
	docker run -i --rm -v $$(pwd):/code -w /code st-scale-toolbox-qa:test black --check app/ || true

# Note to help my future self:
#	Single $ has special meaning in make file.  To make a single $ need two $$.
#	Need that tab to create indentations vs plain ole spaces
#prod.buildapp: @ Build docker image for app
prod.buildapp:
	@echo "\n${BLUE}Building Docker image for app ...${NC}\n"
	docker build --file Dockerfile --target app -t st-scale-toolbox:app .

#prod.runapp: @ Run docker image interactively for app
prod.runapp:
	@echo "\n${BLUE}Run and attached to container ...${NC}\n"
	docker run -it --rm -v $$(pwd)/config:/toolbox/config -v $$(pwd)/project:/toolbox/project st-scale-toolbox:app bash

#prod.runappdetached: @ Run docker image in detached mode
prod.runappdetached:
	@echo "\n${BLUE}Run and attached to container ...${NC}\n"
	docker run -itd --rm -v $$(pwd)/config:/toolbox/config -v $$(pwd)/project:/toolbox/project st-scale-toolbox:app bash