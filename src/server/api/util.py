"""API Utilities"""

from dataclasses import asdict
from flask import abort, url_for
from http import HTTPStatus
from typing import Any

# from ..drivers import DriverData
from server.store import db

def package_result(result):
    return {
        "errorCode": 0,
        "message": "Operation completed successfully",
        "data": result
    }

def package_error(error):
    return {
        "errorCode": error.error_code,
        "message": error.message,
    }

# def driver_data_to_model_properties(driver_data: DriverData) -> dict[str, Any]:
#     data = { k: v for k, v in asdict(driver_data).items() if k in Device.__table__.columns }
#     # Fix up services from list[str] to a comma-delimited str
#     data["services"] = ",".join(data["services"])
#     return data

# def build_device_asset_url(device_id: int, asset_id: str, full_url: bool = False) -> str:
#     return url_for(".get_device_asset", device_id=device_id, asset_id=asset_id, _external=full_url)

# def asset_ids_to_asset_urls(device_id: int, asset_ids: dict[str, str]) -> dict[str, str]:
#     assets = {}
#     for asset_id in asset_ids:
#         assets[asset_id] = build_device_asset_url(device_id, asset_id) #, full_url=True)
#     return assets

def get_or_404(user_id: int, entity, id: int):
    result = db.get_or_404(entity, id)
    if result.user_id != user_id:
        abort(HTTPStatus.NOT_FOUND)
    return result
