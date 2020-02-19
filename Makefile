VERSION ?= 3.6
RUNTIME ?= python

build:
	docker build \
	-t 3mcloud/lambda-packager:$(RUNTIME)-$(VERSION) \
	-f $(RUNTIME)/$(VERSION)/Dockerfile $(RUNTIME)/.

push:
	docker push 3mcloud/lambda-packager:$(RUNTIME)-$(VERSION)

publish: build push

test: build
	rm -rf ${PWD}/tests/$(RUNTIME)/*.zip
	docker run \
		-w /test \
		-v ${PWD}/tests/$(RUNTIME):/test \
		3mcloud/lambda-packager:$(RUNTIME)-$(VERSION) /bin/sh -c "chmod +x ./test.sh && ./test.sh"
