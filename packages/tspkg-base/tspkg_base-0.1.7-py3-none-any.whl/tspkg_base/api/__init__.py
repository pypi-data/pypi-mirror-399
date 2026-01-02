"""
API Register Module

Provides router registe.
"""

from tspkg_base.api.fastapi_route_registry import register_fastapi, add_fastapi_route, register_flask, add_flask_blueprint

__all__ = [
    "register_fastapi",
    "add_fastapi_route",
    "register_flask",
    "add_flask_blueprint"
]
