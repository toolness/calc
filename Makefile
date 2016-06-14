manage ?= python manage.py
test_cmd ?= py.test
port ?= 8081
test_default_options ?= --liveserver=localhost:$(port)
lt_run ?= ./node_modules/.bin/lt-run
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
	$(test_cmd) selenium_tests \
		-x --noinput \
		$(test_default_options) \
		$(options)

test-sauce: static node_modules
	$(lt_run) --port $(port) \
		-- $(test_cmd) selenium_tests \
		-x --noinput \
		$(test_default_options) \
		$(options)

node_modules:
	npm install

static:
	@# using --link allows us to work on the JS and CSS
	@# without having to run collectstatic to see changes
	$(manage) collectstatic --noinput --link > /dev/null

clean:
	rm -rf static

.PHONY: test test-frontend test-backend test-browsers static
