# Working with CALC

## Coding Standards

We adhere to [PEP8](https://www.python.org/dev/peps/pep-0008/) for Python code
formatting. Before committing, please use a linter to ensure that your changes
do not introduce any PEP8 warnings or errors. Most major code editors have a PEP8
integration, such as [linter-pep8](https://atom.io/packages/linter-pep8) for Atom.

## Testing
To run the tests, just run:

```sh
make test
```

If you want to run Python unit tests only:
```sh
make test-backend
```

### Front End Testing
By default, front end tests are done with [Selenium] and [PhantomJS].
To run the front end tests locally, you can just run:

```sh
make test-frontend
```

## Public domain

This project is in the public domain within the United States, and
copyright and related rights in the work worldwide are waived through
the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0
dedication. By submitting a pull request, you are agreeing to comply
with this waiver of copyright interest.
