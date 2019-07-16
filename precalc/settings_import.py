from django.conf import settings
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wikirace.settings")