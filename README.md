# CALC

[![Build Status](https://travis-ci.org/18F/calc.svg?branch=develop)](https://travis-ci.org/18F/calc)
[![Code Climate](https://codeclimate.com/github/18F/calc/badges/gpa.svg)](https://codeclimate.com/github/18F/calc)
[![Test Coverage](https://codeclimate.com/github/18F/calc/badges/coverage.svg)](https://codeclimate.com/github/18F/calc/coverage)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/68ae46ef5bd84f7db471f67ba3ca7f03/snapshot/origin:develop:HEAD/badge.svg)](https://www.quantifiedcode.com/app/project/68ae46ef5bd84f7db471f67ba3ca7f03/snapshot/origin:develop:HEAD)

CALC (formerly known as "Hourglass"), which stands for Contracts Awarded Labor Category, is a tool to help contracting personnel estimate their per-hour labor costs for a contract, based on historical pricing information. The tool is live at [https://calc.gsa.gov](https://calc.gsa.gov). You can track our progress on our [trello board](https://trello.com/b/LjXJaVbZ/prices) or file an issue on this repo.

## Setup

To install the requirements, use:

```sh
pip install -r requirements.txt
```

CALC is a [Django] project. You can configure everything by running:

```sh
cp .env.sample .env
```

Edit the `.env` file to contain your local database configuration, and run:

```sh
./manage.py syncdb
```

to set up the database. After that, you can load all of the data by running:

```sh
./manage.py load_data
./manage.py load_s70
```

From there, you're just a hop, skip and a jump away from your own dev server:

```sh
./manage.py runserver
```

If you are managing https://calc.gsa.gov or any other cloud.gov-based
deployment, see [`deploy.md`][].

## Testing

To run all tests:

```sh
py.test
```

To run all tests and generate a coverage report:

```sh
py.test --cov
```

For more information on running only specific tests, see
[`py.test` Usage and Invocations][pytest].

## CSS

We use [SASS][] for our CSS needs.

To build SASS:

```sh
cd hourglass_site/static/hourglass_site
make
```

To continuously watch SASS for changes and rebuild:

```sh
cd hourglass_site/static/hourglass_site
make watch-style
```

Note that if you're using Docker for development, SASS will automatically
be rebuilt for you.

## Using Docker (optional)

A Docker setup potentially makes development and deployment easier.

To use it, install [Docker][] and [Docker Compose][] and read the
[18F Docker guide][] if you haven't already.

Then run:

```sh
docker-compose build
docker-compose run app python manage.py syncdb
docker-compose run app python manage.py load_data
```

Once the above commands are successful, run:

```sh
docker-compose up
```

This will start up all required servers in containers and output their
log information to stdout. You should be able to visit http://localhost:8000/
directly to access the site.

### Accessing the app container

You'll likely want to run `manage.py` or `py.test` to do other things at
some point. To do this, it's probably easiest to run:

```sh
docker-compose run app bash
```

This will run an interactive bash session inside the main app container.
In this container, the `/calc` directory is mapped to the root of
the repository on your host; you can run `manage.py` or `py.test` from there.

Note that if you don't have Django installed on your host system, you
can just run `python manage.py` directly from outside the container--the
`manage.py` script has been modified to run itself in a Docker container
if it detects that Django isn't installed.

### Updating the containers

All the project's dependencies, such as those mentioned in `requirements.txt`,
are contained in Docker container images.  Whenever these dependencies change,
you'll want to re-run `docker-compose build` to rebuild the containers.

## Environment Variables

Unlike traditional Django settings, we use environment variables
for configuration to be compliant with [twelve-factor][] apps.

You can define environment variables using your environment, or an `.env` file
in the root directory of the repository. For more information on configuring
environment variables on cloud.gov, see [`deploy.md`][].

**Note:** When an environment variable is described as representing a
boolean value, if the variable exists with *any* value (even the empty
string), the boolean is true; otherwise, it's false.

* `DEBUG` is a boolean value that indicates whether debugging is enabled
  (this should always be false in production).

* `SECRET_KEY` is a large random value corresponding to Django's
  [`SECRET_KEY`][] setting. It is automatically set to a known, insecure
  value when `DEBUG` is true.

* `DATABASE_URL` is the URL for the database, as per the
  [DJ-Database-URL schema][].

* `ENABLE_SEO_INDEXING` is a boolean value that indicates whether to
  indicate to search engines that they can index the site.

* `UAA_CLIENT_ID` is your cloud.gov/Cloud Foundry UAA client ID. It
  defaults to `calc-dev`.

* `UAA_CLIENT_SECRET` is your cloud.gov/Cloud Foundry UAA client secret.
  If this is undefined and `DEBUG` is true, then a built-in Fake UAA Provider
  will be used to "simulate" cloud.gov login.

## Staff Login

Staff can log in to CALC for administrative tasks, but accounts
for each user must be manually created either via `manage.py createsuperuser`
or the admin UI itself.

We use cloud.gov/Cloud Foundry's User Account and Authentication (UAA)
server to authenticate users. When a user logs in via UAA, their email
address is looked up in Django's user database; if a matching email is
found, the user is logged in. If not, however, the user is *not* logged in,
and will be shown an error message.

## API

If you're interested in the underlying data, please see https://github.com/18F/calc/blob/master/updating_data.md

### Rates API
You can access rate information at `http://localhost:8000/api/rates/`.

#### Labor Categories
You can search for prices of specific labor categories by using the `q`
parameter. For example:

```
http://localhost:8000/api/rates/?q=accountant
```

You can change the way that labor categories are searched by using the
`query_type` parameter, which can be either:

* `match_words` (the default), which matches all words in the query;
* `match_phrase`, which matches the query as a phrase; or
* `match_exact`, which matches labor categories exactly

You can search for multiple labor categories separated by a comma.

```
http://localhost:8000/api/rates/?q=trainer,instructor
```

All of the query types are case-insenstive.

#### Education and Experience Filters
###### Experience
You can also filter by the minimum years of
experience and maximum years of experience. For example:

```
http://localhost:8000/api/rates/?&min_experience=5&max_experience=10&q=technical
```

Or, you can filter with a single, comma-separated range.
For example, if you wanted results with more than five years and less
than ten years of experience:

```
http://localhost:8000/api/rates/?experience_range=5,10
```

###### Education
The valid values for the education endpoints are `HS` (high school), `AA` (associates),
`BA` (bachelors), `MA` (masters), and `PHD` (Ph.D).

There are two ways to filter based on education, `min_education` and `education`.

To filter by specific education levels, use `education`. It accepts one or more
education values as defined above:

```
http://localhost:8000/api/rates/?education=AA,BA
```

You can also get all results that match and exceed the selected education level
by using `min_education`. The following example will return results that have
an education level of MA or PHD:

```
http://localhost:8000/api/rates/?min_education=MA
```

The default pagination is set to 200. You can paginate using the `page`
parameter:

```
http://localhost:8000/api/rates/?q=translator&page=2
```

#### Price Filters
You can filter by price with any of the `price` (exact match), `price__lte`
(price is less than or equal to) or `price__gte` (price is greater than or
equal to) parameters:

```
http://localhost:8000/api/rates/?price=95
http://localhost:8000/api/rates/?price__lte=95
http://localhost:8000/api/rates/?price__gte=95
```

The `price__lte` and `price__gte` parameters may be used together to search for
a price range:

```
http://localhost:8000/api/rates/?price__gte=95&price__lte=105
```

#### Excluding Records
You can also exclude specific records from the results by passing in an `exclude` parameter and a comma separated list of ids:
```
http://localhost:8000/api/rates/?q=environmental+technician&exclude=875173,875749
```

The `id` attribute is available in api response.

#### Other Filters
Other params allow you to filter by the contract schedule of the transaction,
whether or not the vendor is a small business (valid values: `s` [small] and
`o` [other]), and whether or not the vendor works on the contractor or customer
site.

Here is an example with all three parameters (`schedule`, `site`, and
`business_size`) included:

```
http://localhost:8000/api/rates/?schedule=mobis&site=customer&business_size=s
```

For schedules, there are 8 different values that will return results (case
insensitive):

 - Environmental
 - AIMS
 - Logistics
 - Language Services
 - PES
 - MOBIS
 - Consolidated
 - IT Schedule 70

For site, there are only 3 values (also case insensitive):

 - Customer
 - Contractor
 - both

And the `small_business` parameter can be either `s` for small business, or `o`
for other than small business.

[twelve-factor]: http://12factor.net/
[Django]: https://www.djangoproject.com/
[18F Docker guide]: https://pages.18f.gov/dev-environment-standardization/virtualization/docker/
[Docker]: https://www.docker.com/
[Docker Compose]: https://docs.docker.com/compose/
[`SECRET_KEY`]: https://docs.djangoproject.com/en/1.9/ref/settings/#secret-key
[SASS]: http://sass-lang.com/
[`deploy.md`]: https://github.com/18F/calc/blob/master/deploy.md
[DJ-Database-URL schema]: https://github.com/kennethreitz/dj-database-url#url-schema
[pytest]: https://pytest.org/latest/usage.html
