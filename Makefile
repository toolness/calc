manage ?= python manage.py
test_cmd ?= py.test
port ?= 8081
test_default_options ?= --liveserver=localhost:$(port)
options ?=

test: static
	$(test_cmd) \
		$(test_default_options) \
		$(options)

test-backend:
	$(test_cmd) api contracts \
		$(test_default_options) \
		$(options)

test-frontend: static
	$(test_cmd) selenium_tests -x \
		$(test_default_options) \
		$(options)

static:
	@# using --link allows us to work on the JS and CSS
	@# without having to run collectstatic to see changes
	$(manage) collectstatic --noinput --link > /dev/null

clean:
	rm -rf static

.PHONY: test test-frontend test-backend test-browsers static
