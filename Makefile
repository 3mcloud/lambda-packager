export DOCKER_BUILDKIT=1
IMAGE_NAME:=3mcloud/lambda-packager
VERSION ?= 3.9
RUNTIME ?= python
flags?=

build:
	docker build \
		$(flags) \
		-t $(IMAGE_NAME):$(RUNTIME)-$(VERSION) \
		-f $(RUNTIME)/$(VERSION)/Dockerfile $(RUNTIME)/.

bash:
	make build flags=$(flags)
	docker run -it --rm \
		-w /src \
		-v $(if ${PWD},${PWD},${CURDIR}):/src \
		$(IMAGE_NAME):$(RUNTIME)-$(VERSION) /bin/sh

test:
	make build flags=$(flags)
	docker run --rm \
		-w /test \
		-v $(if ${PWD},${PWD},${CURDIR})/$(RUNTIME):/test \
		$(IMAGE_NAME):$(RUNTIME)-$(VERSION) /bin/sh -c "rm -rf *.zip && chmod +x ./test.sh && ./test.sh"

docs:
	rm -rdf _docs/
	sphinx-build -aE -v -b html docs _docs

.PHONY: docs
