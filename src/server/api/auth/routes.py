import time

from flask import Blueprint
from flask import render_template, redirect, session, url_for
# from werkzeug.security import gen_salt

# from authlib.integrations.flask_oauth2 import current_token
# from authlib.oauth2 import OAuth2Error

# from .models import db, User, OAuth2Client
# from .oauth2 import authorization, require_oauth

# from ..errors import AuthError

from .oauth2 import context

bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder="templates")

# @bp.route("/login", methods=["POST"])
# def login():
#     redirect_uri = url_for('authorize', _external=True)
#     return oauth.twitter.authorize_redirect(redirect_uri)

# @bp.route("/authorize", methods=["GET", "POST"])
# def authorize():
#     token = oauth.twitter.authorize_access_token()
#     resp = oauth.twitter.get('account/verify_credentials.json')
#     resp.raise_for_status()
#     profile = resp.json()
#     # do something with the token and profile
#     return redirect('/')

@bp.route("/")
def homepage():
    user = session.get("user")
    return render_template("home.html", user=user)


@bp.route("/login")
def login():
    oauth_provider = context.oauth_provider
    redirect_uri = url_for("auth.auth", _external=True)
    return oauth_provider.authorize_redirect(redirect_uri)


@bp.route("/auth")
def auth():
    oauth_provider = context.oauth_provider
    token = oauth_provider.authorize_access_token()
    session["user"] = token["userinfo"]
    # return redirect("/auth")
    return redirect(url_for("auth.homepage"))


@bp.route("/logout")
def logout():
    session.pop("user", None)
    # return redirect("/auth")
    return redirect(url_for("auth.homepage"))
