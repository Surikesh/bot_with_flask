import os

if os.environ.get('ENV') == 'dev':
    from settings.dev import *
else:
    from settings.prod import *
