ENV_VERSION?=latest
ENGINE_VERSION?=latest
SPECIFIC_TEST?=tests/
SPECIFIC_BENCHMARK?=benchmarks/

DOCKER := $(shell command -v docker 2>/dev/null)

DEBUG ?= 0

PYTEST_DEBUG=

ifeq ($(DEBUG),1)
	PYTEST_DEBUG="--log-cli-level=-1"
endif


.PHONY: tests

all: build tests

build:
ifdef DOCKER_LOGIN
	docker login -u $(DOCKER_LOGIN) -p $(DOCKER_PASSWORD) docker.pkg.github.com
endif
ifdef DOCKER
	docker build --build-arg "ENGINE_VERSION=$(ENGINE_VERSION)" -t interpretability-engine-environment:$(ENV_VERSION) .
endif

build-deploy:
ifdef DOCKER
	docker build --build-arg "ENGINE_VERSION=$(ENGINE_VERSION)" -f build.Dockerfile -t interpretability-engine-deploy-environment:$(ENV_VERSION) .
endif


tests: check-code unit-tests integration-tests

check-code: build
ifdef DOCKER
	docker run --entrypoint /bin/bash  -t interpretability-engine-environment:$(ENV_VERSION) ./misc/check-code.sh
else
	./misc/check-code.sh
endif

unit-tests: build
ifdef DOCKER
	docker run --entrypoint /bin/bash -t interpretability-engine-environment:$(ENV_VERSION) ./misc/unit-tests.sh $(PYTEST_DEBUG) $(SPECIFIC_TEST)
else
	./misc/unit-tests.sh $(PYTEST_DEBUG) $(SPECIFIC_TEST)
endif

integration-tests: build
ifdef DOCKER
	docker run --entrypoint /bin/bash -w /app -t interpretability-engine-environment:$(ENV_VERSION) ./misc/integration-tests.sh
else
	./misc/integration-tests.sh
endif

interpretability-engine-environment:
ifdef DOCKER
	docker run -v /tmp/unsecure-share:/tmp/unsecure-share --entrypoint bash -ti interpretability-engine-environment:$(ENV_VERSION)
endif

deploy: build-deploy
ifdef DOCKER
	docker run -v $$(pwd):/app -e TWINE_USERNAME=$(TWINE_USERNAME) -e TWINE_PASSWORD=$(TWINE_PASSWORD) -t interpretability-engine-deploy-environment:$(ENV_VERSION) bash -c "python3 setup.py sdist bdist_wheel && twine upload dist/*"
else
	python3 setup.py sdist bdist_wheel && twine upload dist/*
endif
