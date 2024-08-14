
import os
from sqlalchemy import URL

# DO NOT use Unsecure Secrets in production environments
# Generate a safe one with:
#     python -c "import os; print repr(os.urandom(24));"
SECRET_KEY = 'dev'

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = URL.create(
    drivername="postgresql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_USER_PASSWORD"),
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME")
)

# Flask-Mail settings
# For smtp.gmail.com to work, you MUST set "Allow less secure apps" to ON in Google Accounts.
# Change it in https://myaccount.google.com/security#connectedapps (near the bottom).
# MAIL_SERVER = 'smtp.gmail.com'
# MAIL_PORT = 587
# MAIL_USE_SSL = False
# MAIL_USE_TLS = True
# MAIL_USERNAME = 'yourname@gmail.com'
# MAIL_PASSWORD = 'password'

# Flask-User settings
# USER_APP_NAME = 'Flask-User starter app'
# USER_EMAIL_SENDER_NAME = 'Your name'
# USER_EMAIL_SENDER_EMAIL = 'yourname@gmail.com'

# ADMINS = [
#     '"Admin One" <admin1@gmail.com>',
# ]

OAUTH2_REFRESH_TOKEN_GENERATOR = True

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")

# EXPLAIN_TEMPLATE_LOADING = True
