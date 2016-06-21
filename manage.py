#!/usr/bin/env python
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hourglass.settings")
    os.environ.setdefault("DDM_CONTAINER_NAME", "app")

    from docker_django_management import execute_from_command_line

    execute_from_command_line(sys.argv)
