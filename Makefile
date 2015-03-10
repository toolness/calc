manage ?= ./manage.py
tests ?=

test:
	$(manage) test \
		--liveserver=localhost:8081-8181 \
		--nologcapture $(tests)

test-frontend: static
	$(manage) test selenium_tests \
		--liveserver=localhost:8081-8181 \
		--nologcapture

test-backend:
	$(manage) test api contracts \
		--nologcapture $(tests)

static:
	@# using --link allows us to work on the JS and CSS
	@# without having to run collectstatic to see changes
	$(manage) collectstatic --link

clean:
	rm -rf static
