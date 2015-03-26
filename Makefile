manage ?= ./manage.py
options ?=

test:
	$(manage) test \
		--liveserver=localhost:8081-8181 \
		--nologcapture $(options)

test-frontend: static
	$(manage) test selenium_tests \
		--liveserver=localhost:8081-8181 \
		--nologcapture $(options)

test-backend:
	$(manage) test api contracts \
		--nologcapture $(options)

static:
	@# using --link allows us to work on the JS and CSS
	@# without having to run collectstatic to see changes
	$(manage) collectstatic --link

clean:
	rm -rf static
