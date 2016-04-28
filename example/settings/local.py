import os
from production import settings as prod_settings
settings = {
    'A': 2,
    'B': ['x', 'y'],
    'URL': 'http://localhost',
}
settings = dict(prod_settings, **settings)
