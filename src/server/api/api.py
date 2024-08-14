"""IOU API"""

from flask import Blueprint, abort, make_response, request, send_file, url_for
# from flask_jwt_extended import current_user, jwt_required, get_jwt_identity
# from flask_login import login_required
# from celery.result import AsyncResult
from http import HTTPStatus

#from ..drivers import BaseDriver
# from ..device_services import DeviceServiceType
from server.store import db
# from . import const, device_tasks
from .errors import ApiError, AuthError, DriverNotFoundError
# from .tasks import get_task_result_handler
from . import util

bp = Blueprint("api", __name__, url_prefix="/api/v1")

def initialize_blueprint(app):
    app.register_blueprint(bp)

# No caching at all for API endpoints.
@bp.after_request
def add_headers(response):
    # Disable caching
    response.cache_control.no_cache = True

    # Allow Location header to be read
    response.headers["Access-Control-Expose-Headers"] = "Location"
    return response

@bp.errorhandler(ApiError)
def handle_api_exception(error):
    error.message = f"{error.message}" + (f": {error.__context__}" if error.__context__ else "")
    return util.package_error(error)

@bp.app_errorhandler(AuthError)
def handle_auth_error(error):
    error.message = f"{error.message}" + (f": {error.__context__}" if error.__context__ else "")
    return util.package_error(error), HTTPStatus.UNAUTHORIZED
