from production import settings as production
settings = {
    'A': 2,
    'B': ['x', 'y'],
}
settings = dict(production, **settings)
