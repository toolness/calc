## Testing
To run the tests, just run:

```sh
make test
```

### Front End Testing
To run the front end tests locally, you can just run:

```sh
make test-frontend
```

By default, front end tests are done with [Selenium] and [PhantomJS]. You can
run cross-browser tests in [Sauce Labs] by adding a `REMOTE_TESTING` dict to
your settings (preferably in `hourglass/local_settings.py`):

```python
REMOTE_TESTING = {
    'enabled': True,                    # if False, tests will be run locally
    'username: 'your-sauce-username',   # required
    'access_key': 'your-sauce-key',     # required
    'capabilities': {
        'browser': 'chrome',            # 'chrome', 'firefox', 'internet explorer'
        'version': '34',                # this is browser-specific, can be 'ANY'
        'platform': 'Windows XP',       # or 'ANY'
    }
}
```

or, if you don't want to keep your username and access key in your settings,
you can set the `REMOTE_TESTING_USERNAME` and `REMOTE_TESTING_ACCESS_KEY`
environment variables.  (`REMOTE_TESTING_BROWSER`,
`REMOTE_TESTING_BROWSER_VERSION` and `REMOTE_TESTING_PLATFORM` are also valid.)
For instance, to run the Sauce tests against Chrome, IE9 and Firefox:

```
REMOTE_TESTING_BROWSER=chrome make test-sauce && \
make test-sauce && \
REMOTE_TESTING_BROWSER=firefox make test-sauce
```

Running `make test-sauce` without any additional environment variables will run
remote tests for the browser specified in your settings. If you don't specify any
`REMOTE_TESTING['capabilities']`, then the tests will be run on IE9 on Windows 7,
which is our lowest common denominator browser target.

## Public domain

This project is in the public domain within the United States, and
copyright and related rights in the work worldwide are waived through
the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0
dedication. By submitting a pull request, you are agreeing to comply
with this waiver of copyright interest.
