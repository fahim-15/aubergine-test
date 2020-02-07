from django.conf import settings

JWT_DEFAULTS = {
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_VERIFY': True,
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': 'FSLPL',
    'JWT_SECRET_KEY': settings.SECRET_KEY,
    'JWT_ALGORITHM': 'HS256',
}
