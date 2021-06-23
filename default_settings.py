import os
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY', None)
FLASK_ENV = 'production'
SECRET_KEY = os.environ.get("SECRET_KEY", None)