import functools
import typing

import flask
from flask import Blueprint

from .app_runtime import AppRuntime
from .typing import HTTP_METHODS_ARGS_TYPE, HTTP_METHODS
import urllib.parse
from everai.app.context import Context, service_context
from everai.constants import HEADER_REQUEST_ID, HEADER_SETUP_PATH


class _Route:
    def __init__(self, path: str, methods: typing.List[HTTP_METHODS], handler: typing.Callable):
        self.path = path
        self.methods = methods
        self.handler = handler


class Service:
    _routes: typing.List[_Route]
    runtime: AppRuntime

    def __init__(self):
        self._routes = []

    @property
    def routes(self):
        return self._routes

    def __repr__(self):
        lines = []
        for route in self._routes:
            methods = ','.join(route.methods)
            lines.append(f'{methods:<16} {route.path:<25} {route.handler.__name__}')

        return '\n'.join(lines)

    def service_wrapper(self, func, path: str, methods: typing.List[HTTP_METHODS], flask_app: flask.Flask):
        quoted_path = urllib.parse.quote_plus(path, safe='')

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request_id = flask.request.headers.get(HEADER_REQUEST_ID, None)
            # remove request_id check for local test
            # if request_id is None:
            #    raise flask.HTTPBadRequest(f'{HEADER_REQUEST_ID} is required')

            with service_context(self.runtime.context()):
                result = func(*args, **kwargs)

            update_headers = {
                HEADER_SETUP_PATH: quoted_path,
            }
            if request_id is not None:
                update_headers[HEADER_REQUEST_ID] = request_id

            response = flask_app.make_response(result)
            assert isinstance(response, flask_app.response_class)
            response.headers.update(update_headers)
            return response

        return wrapper

    def create_handler(self, flask_app: flask.Flask) -> bool:
        app_blueprint = Blueprint('app', __name__)

        has_some_routes = False

        for route in self.routes:
            service_func = self.service_wrapper(route.handler, path=route.path, methods=route.methods, flask_app=flask_app)
            app_blueprint.add_url_rule(route.path, endpoint=None, methods=route.methods, view_func=service_func)
            has_some_routes = True

        if has_some_routes:
            flask_app.register_blueprint(app_blueprint)

        return has_some_routes

    def route(self, path: str = '/', methods: HTTP_METHODS_ARGS_TYPE = 'GET'):
        def decorator(func):
            _methods = [methods] if isinstance(methods, str) else list[HTTP_METHODS](methods)
            self._routes.append(_Route(path=path, methods=_methods, handler=func))
            return func
        return decorator

    def command(self, prefix: str = '/', port: int = 80):
        # run a command and pass all matched request to indicated port
        ...
