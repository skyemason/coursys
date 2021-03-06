DEPLOY_MODE = 'proddev'

import os
MOSS_DISTRIBUTION_PATH = os.path.join(os.environ['HOME'], 'moss')
DB_BACKUP_DIR = os.path.join(os.environ['COURSYS_DATA_ROOT'], 'db_backup')
SUBMISSION_PATH = os.path.join(os.environ['COURSYS_DATA_ROOT'], 'submitted_files')

CSRF_TRUSTED_ORIGINS = ['localhost:8443']

#DEBUG_TOOLBAR = True
#INTERNAL_IPS = ['127.0.0.1']
#DISABLE_REPORTING_DB = False
#FORCE_CAS = True

# mail to a smtp4dev server: mail viewable at http://localhost:8025
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 2525
EMAIL_USE_SSL = False
