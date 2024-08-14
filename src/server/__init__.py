"""IOU Server Application"""

import os
import logging

from flask import Flask
from flask_compress import Compress
from flask_cors import CORS

from authlib.integrations.flask_client import OAuth

from . import settings #, celery_settings

from .debugger import initialize_debug_server_if_needed
initialize_debug_server_if_needed()
#initialize_debug_server_if_needed(wait_for_client=True, break_on_attach=True)

__version__ = "0.1.0"

_LOGGER = logging.getLogger(__name__)

class ContextFilter(logging.Filter):
    def filter(self, record):
        record.name = record.name.replace("/holm/app/app/", "")
        return True

def setup_logging(app: Flask):
    level = logging.DEBUG if app.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")

    filter = ContextFilter()
    for handler in logging.root.handlers:
        handler.addFilter(filter)

    # Make certain loggers less verbose
    # logger_to_silence = ("celery", "easysnmp.interface")
    logger_to_silence = ()
    for logger in logger_to_silence:
        logging.getLogger(logger).setLevel(logging.INFO)

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.json.sort_keys = False
    app.config.from_object(settings)

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    setup_logging(app)

    # from app.tasks import task_manager
    from server.store import db
    from server.api import models
    db.init_app(app)
    with app.app_context():
        db.create_all()

    from server.api import register_blueprints
    register_blueprints(app)

    CORS(app)
    Compress(app)

    # if app.debug:
        # init_db(app)

    return app


def init_db(app):
    from .store import User, db

    with app.app_context():
        # Add admin user (with 'admin' password), if one is not available
        user = db.session.execute(db.select(User)
            .where(User.email == "admin")).one_or_none()
        if not user:
            user = User(name="Administrator", password="admin", email="admin")
            _LOGGER.info("Adding admin user")
            db.session.add(user)
            db.session.commit()

            # Add frontend client id
            # init_client(db, user.id)

        # user = db.session.execute(db.select(User)
        #     .filter_by(email=app.config["TEST_USER_EMAIL"])).first()
        # if user is None:
        #     user = User(
        #         name=app.config["TEST_USER_NAME"],
        #         password=app.config["TEST_USER_PASSWORD"],
        #         email=app.config["TEST_USER_EMAIL"]
        #         )
        #     print(f"Adding user {user}")
        #     db.session.add(user)

        #     for device_info in app.config["TEST_DEVICES"]:
        #         device = Device()
        #         for k, v in device_info.items():
        #             setattr(device, k, v)
        #         print(f"Adding device {device}")
        #         user.devices.append(device)

# def init_client(db, user_id):
#     import time
#     from werkzeug.security import gen_salt
#     from app.api.auth import OAuth2Client

#     client_id = gen_salt(24)
#     client_id_issued_at = int(time.time())
#     client = OAuth2Client(
#         client_id=client_id,
#         client_id_issued_at=client_id_issued_at,
#         user_id=user_id,
#     )

#     client_metadata = {
#         "client_name": "front_end",
#         "client_uri": "http://github.com/brunokc/holm",
#         "grant_types": ["authorization_code", "password"],
#         "redirect_uris": ["http://github.com/brunokc/holm"],
#         "response_types": ["code"],
#         "scope": "profile",
#         "token_endpoint_auth_method": "client_secret_basic"
#     }
#     client.set_client_metadata(client_metadata)

#     # if form["token_endpoint_auth_method"] == "none":
#     #     client.client_secret = ""
#     # else:
#     client.client_secret = gen_salt(48)

#     db.session.add(client)
#     db.session.commit()
