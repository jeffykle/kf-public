import io
import os

# Pulling django-environ settings file, stored in Secret Manager
import environ
import google.auth
from google.cloud import secretmanager as sm

from .base import *

try:
    from .local import *
except ImportError:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.path.join(BASE_DIR,  ".env")

SETTINGS_NAME = "application_settings"

env = environ.Env()

_, project = google.auth.default()
client = sm.SecretManagerServiceClient()
name = f"projects/861301376037/secrets/application_settings/versions/latest"
payload = client.access_secret_version(request={"name":name}).payload.data.decode("UTF-8")
env.read_env(io.StringIO(payload))

# Setting this value from django-environ
SECRET_KEY = env("SECRET_KEY")

# Could be more explicitly set (see "Improvements")
ALLOWED_HOSTS = ["*"]

# Default false. True allows default landing pages to be visible
DEBUG = False

# Setting this value from django-environ
DATABASES = {"default": env.db()}
# DATABASES["default"]["PORT"] = "3306"
# DATABASES["default"]["HOST"] = "127.0.0.1"

INSTALLED_APPS += ["storages"] # for django-storages


# Define static storage via django-storages[google]
GS_BUCKET_NAME = env("GS_BUCKET_NAME")
STATICFILES_DIRS = []
DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
STATICFILES_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
GS_DEFAULT_ACL = "publicRead"

BRAINTREE_PRODUCTION = False


EMAIL_HOST = env('EMAIL_HOST')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
BRAINTREE_MERCHANT_ID = env('BRAINTREE_MERCHANT_ID')
BRAINTREE_PUBLIC_KEY = env('BRAINTREE_PUBLIC_KEY')
BRAINTREE_PRIVATE_KEY = env('BRAINTREE_PRIVATE_KEY')
GOOGLE_API_KEY = env('GOOGLE_API_KEY')
RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY')



SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        'APP': {
            'client_id': env('GOOGLE_APP_CLIENT_ID'),
            'secret': env('GOOGLE_APP_SECRET'),
            'key': ''
        },
        'AUTH_PARAMS': {
            'access_type': 'offline',
            'prompt' : 'select_account'
        }
    }
}
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
