import importlib
import os
from pathlib import Path

from django.conf import ENVIRONMENT_VARIABLE as DJANGO_SETTINGS_ENVIRONMENT_VARIABLE

# Setting the BASE_DIR to be the grandparent of the DJANGO_SETTINGS_MODULE
# We assert that the DJANGO_SETTINGS_MODULE is always set and always a proper Python package.
SETTINGS_MODULE = os.environ.get(DJANGO_SETTINGS_ENVIRONMENT_VARIABLE)
assert SETTINGS_MODULE
django_settings_module = importlib.import_module(SETTINGS_MODULE)
assert django_settings_module.__file__

BASE_DIR = Path(django_settings_module.__file__).resolve().parent.parent
