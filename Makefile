ENV_VERSION?=latest
ENGINE_VERSION?=1.0.2
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
ifdef DOCKER
	docker build --build-arg "ENGINE_VERSION=$(ENGINE_VERSION)" -t interepretability-engine-environment:$(ENV_VERSION) .
endif

tests: check-code unit-tests integration-tests

check-code: build
ifdef DOCKER
	docker run -v $$(pwd):/app:ro --entrypoint /bin/bash  -t interepretability-engine-environment:$(ENV_VERSION) ./misc/check-code.sh
else
	./misc/check-code.sh
endif

unit-tests: build
ifdef DOCKER
	docker run -v $$(pwd):/app:ro --entrypoint /bin/bash -t interepretability-engine-environment:$(ENV_VERSION) ./misc/unit-tests.sh $(PYTEST_DEBUG) $(SPECIFIC_TEST)
else
	./misc/unit-tests.sh $(PYTEST_DEBUG) $(SPECIFIC_TEST)
endif

integration-tests: build
ifdef DOCKER
	docker run -v $$(pwd):/app:ro --entrypoint /bin/bash -w /app -t interepretability-engine-environment:$(ENV_VERSION) ./misc/integration-tests.sh
else
	./misc/integration-tests.sh
endif

interpretability-engine-environment:
ifdef DOCKER
	docker run -v /tmp/unsecure-share:/tmp/unsecure-share -v $$(pwd):/app:ro --entrypoint bash -ti interepretability-engine-environment:$(ENV_VERSION)
endif
