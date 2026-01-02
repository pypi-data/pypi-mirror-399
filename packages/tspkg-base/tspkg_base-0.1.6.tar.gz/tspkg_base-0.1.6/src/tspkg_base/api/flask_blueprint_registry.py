_PENDING_FLASK_BLUEPRINTS = []


def register(blueprint, prefix=""):
    """
    Register a Flask blueprint.
    Args
        :param blueprint: Flask blueprint.
        :param prefix: Prefix string to prepend to all URL routes.
    """
    _PENDING_FLASK_BLUEPRINTS.append((blueprint, prefix))


def add_flask_blueprint(app):
    """
    Add all registered Flask blueprints to the Flask app.
    Args:
        :param app: Flask app.
    """
    for blueprint, prefix in _PENDING_FLASK_BLUEPRINTS:
        app.register_blueprint(blueprint, url_prefix=prefix)
