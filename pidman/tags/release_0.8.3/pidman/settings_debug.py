from settings import *
DEBUG = True
INTERNAL_IPS = ['YOUR IP HERE']
MIDDLEWARE_CLASSES += ('djangologging.middleware.LoggingMiddleware',)
LOGGING_LOG_SQL = True
