#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

    # Set Settings file
    os.environ.setdefault( "DJANGO_SETTINGS_MODULE", 'vron._settings.custom' )


    # Execute from command line
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)