"""Authentication Support"""

# OAuth2 Server based on the code at https://github.com/authlib/example-oauth2-server

from .oauth2 import config_oauth #, OAuth2Client
from .routes import bp

def initialize_blueprint(app):
    config_oauth(app)
    app.register_blueprint(bp)
