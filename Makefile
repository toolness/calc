manage ?= ./manage.py
port ?= 8081
default_options ?= --nologcapture --liveserver=localhost:$(port)
lt_run ?= ./node_modules/.bin/lt-run
options ?=

test: static
	$(manage) test \
		$(default_options) \
		$(options)

test-backend:
	$(manage) test api contracts \
		$(default_options) \
		$(options)

test-frontend: static
	$(manage) test selenium_tests \
		-x --noinput \
		$(default_options) \
		$(options)

test-sauce: static node_modules
	$(lt_run) --port $(port) \
		-- $(manage) test selenium_tests \
		-x --noinput \
		$(default_options) \
		$(options)

node_modules:
	npm install

static:
	@# using --link allows us to work on the JS and CSS
	@# without having to run collectstatic to see changes
	@# piping "yes" to the command bypasses the prompt,
	@# and piping the output to /dev/null hushes stdout
	echo "yes" | $(manage) collectstatic --link > /dev/null

clean:
	rm -rf static

.PHONY: test test-frontend test-backend test-browsers
