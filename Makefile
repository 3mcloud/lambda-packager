IMAGE_NAME=3mcloud/lambda-packager
VERSION ?= 3.9
RUNTIME ?= python

build:
	docker build \
	-t $(IMAGE_NAME):$(RUNTIME)-$(VERSION) \
	-f $(RUNTIME)/$(VERSION)/Dockerfile $(RUNTIME)/.

bash: build
	docker run -it --rm\
		-w /src \
		-v $(if ${PWD},${PWD},${CURDIR}):/src \
		$(IMAGE_NAME):$(RUNTIME)-$(VERSION) /bin/sh

install:
	pip3 install -r python/requirements-dev.txt

clean-up:
	rm -rf *.zip
	rm -rf python/*.zip

lint:
	python3 -m pylint --fail-under=9 python/entrypoint.py

unit:
	python3 -m pytest -x -s -vvv python/tests/

test: build
	docker run --rm\
		-w /src \
		-v $(if ${PWD},${PWD},${CURDIR}):/src \
		$(IMAGE_NAME):$(RUNTIME)-$(VERSION) /bin/bash -c "make validate"

# setup and run all tests
validate: clean-up install lint unit
