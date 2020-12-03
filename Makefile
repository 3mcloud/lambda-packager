VERSION ?= 3.8
RUNTIME ?= python

build:
	docker build \
	-t 3mcloud/lambda-packager:$(RUNTIME)-$(VERSION) \
	-f $(RUNTIME)/$(VERSION)/Dockerfile $(RUNTIME)/.

test: build
	docker run --rm\
		-w /test \
		-v $(if ${PWD},${PWD},${CURDIR})/$(RUNTIME):/test \
		3mcloud/lambda-packager:$(RUNTIME)-$(VERSION) /bin/sh -c "rm -rf *.zip && chmod +x ./test.sh && ./test.sh"

bash: build
	docker run -it --rm\
		-w /src \
		-v $(if ${PWD},${PWD},${CURDIR}):/src \
		3mcloud/lambda-packager:$(RUNTIME)-$(VERSION) /bin/sh
