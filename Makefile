manage ?= ./manage.py

test:
	$(manage) test

test-frontend: static
	$(manage) test selenium_tests \
		--liveserver=localhost:8081-8181 \
		--nologcapture

static:
	@# using --link allows us to work on the JS and CSS
	@# without having to run collectstatic to see changes
	$(manage) collectstatic --link

clean:
	rm -rf static
