from . import api, auth

def register_blueprints(app):
    for module in (api, auth):
        if hasattr(module, "initialize_blueprint"):
            module.initialize_blueprint(app)
