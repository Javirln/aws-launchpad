#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
import os
import sys

if sys.argv[0] and sys.argv[0].find('django_test_manage.py') != -1:
    import configurations

    configurations.setup()

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config")
    os.environ.setdefault("DJANGO_CONFIGURATION", "Docker")

    from configurations.management import execute_from_command_line

    execute_from_command_line(sys.argv)
