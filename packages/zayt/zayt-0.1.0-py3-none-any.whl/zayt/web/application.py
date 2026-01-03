import asyncio
import traceback
from http import HTTPStatus

import structlog
from asgikit import (
    Request,
    Response,
    WebSocket,
    WebSocketState,
    WebSocketDisconnect,
    WebSocketResponseNotSupportedError,
)

from zayt.conf.settings import Settings, get_settings_meta
from zayt.di.call import call_with_dependencies
from zayt.di.container import Container
from zayt.ext.error import ExtensionMissingInitFunctionError, ExtensionNotFoundError
from zayt.util.base_types import get_base_types
from zayt.util.import_item import import_item
from zayt.util.maybe_async import call_maybe_async
from zayt.web.exception import (
    HTTPStatusException,
    WebSocketException,
    HTTPNotFoundException,
)
from zayt.web.exception_handler.decorator import ExceptionHandlerType
from zayt.web.exception_handler.discover import find_exception_handlers
from zayt.web.lifecycle.discover import find_background_services, find_startup_hooks
from zayt.web.routing.router import Router

logger = structlog.get_logger(__name__)


def _init_settings(settings: Settings | None) -> Settings:
    settings_files = []
    if not settings:
        settings, settings_files = get_settings_meta()

    logging_setup = import_item(settings.logging.setup)
    logging_setup(settings)

    for settings_file, profile, found in settings_files:
        if found:
            logger.info("settings loaded", file=settings_file.name)
        elif profile:
            logger.info("settings file not found", file=settings_file.name)

    return settings


# pylint: disable=too-many-instance-attributes
class Zayt:
    """Entrypoint class for a Zayt Application

    Will try to automatically import and register a module called "application".
    Other modules and classes can be registered using the "register" method
    """

    def __init__(self, settings: Settings = None):
        self.settings = _init_settings(settings)

        self.di = Container()
        self.di.define(Container, self.di)
        self.di.define(Settings, self.settings)

        self.router = Router()
        self.di.define(Router, self.router)

        self.handler = self._request_handler
        self.exception_handlers = find_exception_handlers(self.settings.__application__)
        self._exception_handler_map = {}

        self.startup = find_startup_hooks(self.settings.__application__)

        self.background_services = find_background_services(
            self.settings.__application__
        )
        self._background_services: set[asyncio.Task] = set()

        self.di.scan(self.settings.__application__)
        self.router.scan(self.settings.__application__)

    async def __call__(self, scope, receive, send):
        match scope["type"]:
            case "http" | "websocket":
                await self._handle_request(scope, receive, send)
            case "lifespan":
                await self._handle_lifespan(scope, receive, send)
            case _:
                raise RuntimeError(f"unknown scope '{scope['type']}'")

    async def _initialize_extensions(self):
        for extension_name in self.settings.extensions:
            try:
                extension_init = import_item(f"{extension_name}:init_extension")
            except ImportError:
                # pylint: disable=raise-missing-from
                raise ExtensionNotFoundError(extension_name)
            except AttributeError:
                # pylint: disable=raise-missing-from
                raise ExtensionMissingInitFunctionError(extension_name)

            await call_maybe_async(extension_init, self.di, self.settings)

    async def _initialize_asgi_middleware(self):
        middleware = self.settings.asgi_middleware
        if not middleware:
            return

        middleware_functions = [import_item(name) for name in middleware]

        for factory in reversed(middleware_functions):
            self.handler = await call_with_dependencies(
                self.di, factory, args=[self.handler]
            )

    async def _lifespan_startup(self):
        await self._initialize_extensions()
        await self._initialize_asgi_middleware()

        for hook in self.startup:
            await call_with_dependencies(self.di, hook)

        for hook in self.background_services:
            task = asyncio.create_task(call_with_dependencies(self.di, hook))
            self._background_services.add(task)

            def done_callback(done):
                if err := done.exception():
                    logger.exception(err, exc_info=err)
                self._background_services.discard(done)

            task.add_done_callback(done_callback)

    async def _lifespan_shutdown(self):
        for task in self._background_services:
            if not task.done():
                task.cancel()

        await self.di.finalize()

    async def _handle_lifespan(self, _scope, receive, send):
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                logger.debug("handling lifespan startup")
                try:
                    await self._lifespan_startup()
                    logger.debug("lifespan startup complete")
                    await send({"type": "lifespan.startup.complete"})
                except Exception as err:
                    logger.exception("lifespan startup failed")
                    await send({"type": "lifespan.startup.failed", "message": str(err)})
            elif message["type"] == "lifespan.shutdown":
                logger.debug("handling lifespan shutdown")
                try:
                    await self._lifespan_shutdown()
                    logger.debug("lifespan shutdown complete")
                    await send({"type": "lifespan.shutdown.complete"})
                except Exception as err:
                    logger.debug("lifespan shutdown failed")
                    await send(
                        {"type": "lifespan.shutdown.failed", "message": str(err)}
                    )
                break

    async def _handle_request(self, scope, receive, send):
        try:
            await self.handler(scope, receive, send)
        except WebSocketDisconnect:
            client = scope["client"]
            logger.info(
                "websocket disconnect from client",
                client=f"{client[0]}:{client[1]}",
            )
            await WebSocket(scope, receive, send).close()
        except WebSocketException as err:
            if scope["type"] == "http":
                logger.error("request handler raise WebSocketException")
                response = Response(scope, receive, send)
                if not response.is_started:
                    await response.start(HTTPStatus.INTERNAL_SERVER_ERROR)
                    await response.end()
                elif not response.is_finished:
                    await response.end()
                return

            await WebSocket(scope, receive, send).close(err.code, err.reason)
        except HTTPStatusException as err:
            await self._handle_http_exception(scope, receive, send, err)
        except Exception as err:
            logger.exception("error processing request")

            if scope["type"] == "http":
                trace = "".join(traceback.format_exception(err))
                request = Request(scope, receive, send)
                await request.respond_text(trace, status=500)
            else:
                await WebSocket(scope, receive, send).close(1011)

    async def _request_handler(self, scope, receive, send):
        request = Request(scope, receive, send)
        self.di.define(Request, request, context=request)

        path = request.path
        method = request.method

        if request.is_http:
            logger.debug(
                "handling http request",
                method=method,
                path=path,
                query=request.query,
            )
        else:
            logger.debug(
                "handling websocket",
                path=path,
                query=request.query,
            )

        match = self.router.match(method, path)

        if not match:
            raise HTTPNotFoundException()

        handler = match.route.action
        path_params = match.params
        scope["path_params"] = path_params

        try:
            await call_with_dependencies(
                self.di, handler, args=(request,), context=request
            )

            if request.is_websocket:
                websocket = WebSocket(scope, receive, send)
                if websocket.state != WebSocketState.CLOSED:
                    await websocket.close()
            elif not request.response.is_started:
                await request.respond_empty(HTTPStatus.INTERNAL_SERVER_ERROR)
            elif not request.response.is_finished:
                await request.response.end()
        except Exception as err:
            if request.is_websocket:
                raise

            if handler := self._get_exception_handler(type(err)):
                logger.debug(
                    "Handling exception with exception handler",
                    handler=f"{handler.__module__}.{handler.__qualname__}",
                )

                request = Request(scope, receive, send)
                await call_with_dependencies(
                    self.di, handler, args=(request, err), context=request
                )
            else:
                raise
        finally:
            await self.di.finalize(request)

    def _get_exception_handler(
        self, err: type[BaseException]
    ) -> ExceptionHandlerType | None:
        if handler := self._exception_handler_map.get(err):
            return handler

        for base in get_base_types(err):
            if handler := self.exception_handlers.get(base):
                self._exception_handler_map[err] = handler
                return handler

        return None

    @staticmethod
    async def _handle_http_exception(scope, receive, send, err: HTTPStatusException):
        if cause := err.__cause__:
            logger.error("http exception with cause", exc_info=cause)
            stack_trace = "".join(traceback.format_exception(cause))
        else:
            stack_trace = None

        request = Request(scope, receive, send)

        if request.response.is_finished:
            logger.error("request already finished", exc_info=cause)
            return

        try:
            if stack_trace:
                await request.respond_text(
                    stack_trace, status=err.status, media_type="text/plain"
                )
            else:
                await request.respond_empty(err.status)
        except WebSocketResponseNotSupportedError:
            await WebSocket(scope, receive, send).close(1011 if err.__cause__ else 1006)
            return
