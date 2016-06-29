#!/usr/bin/env python

'''
    Docker Django Management v0.1

    This script/module makes it easier to allow developers to run
    your Django project in a docker container.

    Features:

    * A docker entrypoint always sets the docker user to the same uid
      as the owner of the directory your manage.py is in, ensuring that
      any files created by the docker container have appropriate
      permissions (i.e., deleting them does not require sudo).

    * Ctrl-C can be used during `docker-compose up` to quickly and
      gracefully exit.

    * `manage.py` always waits for the database to be up, ensuring
      there are no race conditions.

    * If Django isn't installed on the host system, `manage.py` can be
      used as a shortcut for `docker-compose run <your Django container's
      name> python manage.py`.

    * Friendly warnings are logged if anything seems to be misconfigured.

    To use it:

    * Place this script in the same directory as your Django project's
      manage.py file.

    * Change the following line of your manage.py file:

          from django.core.management import execute_from_command_line

      to:

          # If your Django container isn't called "app", change this line:
          os.environ.setdefault("DDM_CONTAINER_NAME", "app")

          from docker_django_management import execute_from_command_line

    * Merge the following into the configuration for your Django container
      in your docker-compose.yml:

          volumes:
            - .:/app
          working_dir: /app
          entrypoint: python /app/docker_django_management.py
          environment:
            - DDM_IS_RUNNING_IN_DOCKER=yup
            - PYTHONUNBUFFERED=yup
          command: python manage.py runserver 0.0.0.0:8000
          ports:
            - "8000:8000"

    You'll also want to make sure your docker-compose.yml configures
    your database and any other services properly, of course.

    Once everything is set up, developers can start your Django
    project via `docker-compose up`.
'''

import os
import sys
import pwd
import time
import signal
import subprocess


MY_DIR = os.path.abspath(os.path.dirname(__file__))
HOST_UID = os.stat(MY_DIR).st_uid

HOST_USER = os.environ.get('DDM_HOST_USER', 'docker_user')
CONTAINER_NAME = os.environ.get('DDM_CONTAINER_NAME')
IS_RUNNING_IN_DOCKER = 'DDM_IS_RUNNING_IN_DOCKER' in os.environ


def warn(msg):
    '''
    Prints a warning message in red.
    '''

    print(
        "\x1b[31;1m"  # Red
        "WARNING: " + msg +
        "\x1b[0m"     # Reset colors
    )
    sys.stdout.flush()


def setup_docker_sigterm_handler():
    '''
    'manage.py runserver' is not set up to deal with a SIGTERM signal,
    and instead expects a Ctrl-C to come to its child process. So we'll
    add a SIGTERM handler here that finds all our children and gracefully
    shuts them down, which provides a quick graceful exit from Docker.
    '''

    def get_children():
        output = subprocess.check_output(
            "ps --ppid=%d -o pid | awk 'NR>1' | xargs echo" % os.getpid(),
            shell=True
        )
        return map(int, output.split())

    def handler(signum, frame):
        for child_pid in get_children():
            try:
                os.kill(child_pid, signal.SIGTERM)
                os.waitpid(child_pid, 0)
            except OSError:
                pass
        sys.exit(0)

    print("Setting up Docker SIGTERM handler for quick, graceful exit.")
    signal.signal(signal.SIGTERM, handler)


def wait_for_db(max_attempts=15, seconds_between_attempts=1):
    '''
    Some manage.py commands interact with the database, and we want
    them to be directly callable from `docker-compose run`. However,
    because docker may start the database container at the same time
    as it runs `manage.py`, we potentially face a race condition, and
    the manage.py command may attempt to connect to a database that
    isn't yet ready for connections.

    To alleviate this, we'll just wait for the database before calling
    the manage.py command.
    '''

    from django.db import DEFAULT_DB_ALIAS, connections
    from django.db.utils import OperationalError

    connection = connections[DEFAULT_DB_ALIAS]
    attempts = 0

    while True:
        try:
            connection.ensure_connection()
            break
        except OperationalError as e:
            if attempts >= max_attempts:
                raise e
            attempts += 1
            time.sleep(seconds_between_attempts)
            print("Attempting to connect to database.")

    print("Connection to database established.")


def execute_from_command_line(argv):
    '''
    This is like django.core.management.execute_from_command_line,
    but if the django package is unavailable, the script executes itself
    inside a docker container, where the django package is assumed
    to be available.

    Ultimately, this allows developers to use manage.py from their host
    system without needing to prefix all of their commands with
    'docker-compose run <container name>'.
    '''

    is_runserver = len(argv) > 1 and argv[1] == 'runserver'

    if IS_RUNNING_IN_DOCKER:
        if is_runserver:
            setup_docker_sigterm_handler()
        wait_for_db()

        if not 'PYTHONUNBUFFERED' in os.environ:
            warn("PYTHONUNBUFFERED is not defined. Some output may "
                 "not be visible.")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as e:
        if not CONTAINER_NAME:
            raise e
        # Assume the user wants to run us in docker.
        if is_runserver:
            # Even with --service-ports, by default runserver only exposes
            # itself on 127.0.0.1, which docker can't expose to the
            # host through its networking stack. It's easiest to just
            # tell the developer to use 'docker-compose up' instead.
            warn("You should probably be using 'docker-compose up' "
                 "to run the server.")
        try:
            os.execvp('docker-compose', [
                'docker-compose', 'run', CONTAINER_NAME, 'python'
            ] + argv)
        except OSError:
            # Apparently docker-compose isn't installed, so just raise
            # the original ImportError.
            raise e

    execute_from_command_line(argv)


def does_username_exist(username):
    '''
    Returns True if the given OS username exists, False otherwise.
    '''

    try:
        pwd.getpwnam(username)
        return True
    except KeyError:
        return False


def does_uid_exist(uid):
    '''
    Returns True if the given OS user id exists, False otherwise.
    '''

    try:
        pwd.getpwuid(uid)
        return True
    except KeyError:
        return False


def entrypoint(argv):
    '''
    This is a Docker entrypoint that configures the container to run
    as the same uid of the user on the host container, rather than
    the Docker default of root. Aside from following security best
    practices, this makes it so that any files created by the Docker
    container are also owned by the same user on the host system.
    '''

    if HOST_UID != os.geteuid():
        if not does_uid_exist(HOST_UID):
            username = HOST_USER
            while does_username_exist(username):
                username += '0'
            home_dir = '/home/%s' % username
            subprocess.check_call([
                'useradd',
                '-d', home_dir,
                '-m', username,
                '-u', str(HOST_UID)
            ])
        os.environ['HOME'] = '/home/%s' % pwd.getpwuid(HOST_UID).pw_name
        os.setuid(HOST_UID)
    os.execvp(argv[1], argv[1:])


if __name__ == "__main__":
    entrypoint(sys.argv)
