# from datetime import datetime

from authlib.integrations.flask_client import OAuth

# from authlib.integrations.flask_oauth2 import (
#     AuthorizationServer,
#     ResourceProtector,
# )

from types import SimpleNamespace

context = SimpleNamespace()

def config_oauth(app):
    context.oauth = OAuth(app)

    context.oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid email profile"
        }
    )

    # From ChatGPT
    # context.oauth.register(
    #     name='microsoft',
    #     client_id=client_id,
    #     client_secret=client_secret,
    #     authorize_url=f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize',
    #     authorize_params=None,
    #     access_token_url=f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token',
    #     access_token_params=None,
    #     refresh_token_url=None,
    #     redirect_uri='http://localhost:5000/auth/callback',  # Replace with your redirect URI
    #     client_kwargs={'scope': 'User.Read'}
    # )

    # This can be simplified by having Authlib obtain this information using Microsoft's server
    # metadata URL https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration
    # The tenant ID can have special values:
    # "common": allow for authentication of personal MSAs and AzureAD/EntraID accounts
    # "consumers": allow for authentication of personal MSAs only
    context.oauth.register(
        name="microsoft",
        server_metadata_url="https://login.microsoftonline.com/consumers/v2.0/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid email profile"
        }
    )

    # context.oauth.register(
    #     name="github",
    #     client_id="{{ your-github-client-id }}",
    #     client_secret="{{ your-github-client-secret }}",
    #     access_token_url="https://github.com/login/oauth/access_token",
    #     access_token_params=None,
    #     authorize_url="https://github.com/login/oauth/authorize",
    #     authorize_params=None,
    #     api_base_url="https://api.github.com/",
    #     client_kwargs={"scope": "user:email"},
    # )

    context.oauth_provider = context.oauth.microsoft
