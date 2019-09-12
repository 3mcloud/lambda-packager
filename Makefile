VERSION ?= 3.6
RUNTIME ?= python

build:
	docker build \
	-t 3mcloud/lambda-packager:$(RUNTIME)-$(VERSION) \
	-f $(RUNTIME)/$(VERSION)/Dockerfile python/$(VERSION)/.

push:
	docker push 3mcloud/lambda-packager:$(RUNTIME)-$(VERSION)

publish: build push

test: build
	rm -rf ${PWD}/tests/$(RUNTIME)/$(VERSION)/deployment.zip
	docker run \
		-w /test \
		-v ${PWD}/tests/$(RUNTIME)/$(VERSION):/test \
		3mcloud/lambda-packager:$(RUNTIME)-$(VERSION) ./test.sh
