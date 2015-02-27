import logging
import logging.config
import os

FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
DEBUG = FLASK_ENV == "development"

if DEBUG:
    SECRET_KEY = "aoen79aslcoehul-9gaoesnuthaznoetuhsra8oeus"
else:
    SECRET_KEY = os.environ['FLASK_SECRET_KEY']

SQLALCHEMY_DATABASE_URI = 'sqlite:///../instance/tmp.db'

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(process)-6d %(name)-12s %(levelname)-8s %(message)s',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG'
    },
    'loggers': {
        'elections': {
            'level': 'DEBUG',
        },
    }
})
