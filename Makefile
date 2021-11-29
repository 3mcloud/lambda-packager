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

test: build
	docker run --rm\
		-w /test \
		-v $(if ${PWD},${PWD},${CURDIR})/$(RUNTIME):/test \
		$(IMAGE_NAME):$(RUNTIME)-$(VERSION) /bin/sh -c "rm -rf *.zip && chmod +x ./test.sh && ./test.sh"
