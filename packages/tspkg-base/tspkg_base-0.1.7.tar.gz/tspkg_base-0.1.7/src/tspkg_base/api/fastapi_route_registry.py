_PENDING_FASTAPI_ROUTERS = []


def register_fastapi(router, prefix=""):
    """
    Register a FastAPI router.
    Args
        :param router: FastAPI router.
        :param prefix: Prefix string to prepend to all URL routes.
    """
    _PENDING_FASTAPI_ROUTERS.append((router, prefix))


def add_fastapi_route(app):
    for router, prefix in _PENDING_FASTAPI_ROUTERS:
        """
        Add a FastAPI route to the FastAPI app.
        Args:
            :param app: fastapi app.
        """
        app.include_router(router, prefix=prefix)
