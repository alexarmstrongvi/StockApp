import os
ALPHA_VANTAGE_API_KEY = os.environ['ALPHA_VANTAGE_API_KEY']
FLASK_ENV = 'production'
SECRET_KEY = os.environ.get("SECRET_KEY", None)