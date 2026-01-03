import os
from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path

from asgikit import Request

from zayt.conf import Settings
from zayt.web.exception import HTTPNotFoundException


def static_files_middleware(app, settings: Settings):
    settings = settings.staticfiles
    path = settings.path.lstrip("/")
    root = Path(settings.root).resolve().absolute()

    # dict of file path to (content-type, content-length, last-modified)
    filelist: dict[str, os.stat_result] = {}

    for dirpath, _dirnames, filenames in os.walk(root):
        for filename in filenames:
            file = os.path.join(dirpath, filename)
            stat_result = os.stat(file)
            filelist[file] = stat_result

    mappings = {
        name.lstrip("/"): os.path.join(root, value.lstrip("/"))
        for name, value in settings.get("mappings", {}).items()
    }

    if difference := set(mappings.values()).difference(filelist):
        files = ", ".join(difference)
        raise ValueError(f"Static files mappings not found: {files}")

    return StaticFilesMiddleware(app, path, root, filelist, mappings)


def uploaded_files_middleware(app, settings: Settings):
    settings = settings.uploadedfiles
    path = settings.path.lstrip("/")
    root = Path(settings.root).resolve()
    return UploadedFilesMiddleware(app, path, root)


class BaseFilesMiddleware(ABC):
    def __init__(self, app: Callable, path: str, root: Path):
        self.app = app
        self.path = path if path.endswith("/") else path + "/"
        self.root = root

    @abstractmethod
    def get_file_to_serve(
        self, scope: dict
    ) -> tuple[str, os.stat_result | None] | None:
        pass

    async def __call__(self, scope, receive, send):
        if (scope["type"] == "http") and (result := self.get_file_to_serve(scope)):
            file_to_serve, stat_result = result
            file_to_serve = (self.root / file_to_serve).resolve()

            if not (
                file_to_serve.is_file() and file_to_serve.is_relative_to(self.root)
            ):
                raise HTTPNotFoundException()

            request = Request(scope, receive, send)
            await request.respond_file(file_to_serve, stat_result=stat_result)
        else:
            await self.app(scope, receive, send)


class UploadedFilesMiddleware(BaseFilesMiddleware):
    def get_file_to_serve(self, scope: dict) -> tuple[str, None] | None:
        request_path = scope["path"].lstrip("/")

        if request_path.startswith(self.path):
            return request_path.removeprefix(self.path).lstrip("/"), None

        return None


class StaticFilesMiddleware(BaseFilesMiddleware):
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        app,
        path: str,
        root: Path,
        filelist: dict[str, os.stat_result],
        mappings: dict[str, str],
    ):
        super().__init__(app, path, root)
        self.filelist = filelist
        self.mappings = mappings

    def get_file_to_serve(self, scope: dict) -> tuple[str, os.stat_result] | None:
        request_path = scope["path"].lstrip("/")

        file_to_serve = None
        if file_path := self.mappings.get(request_path):
            file_to_serve = file_path
        elif request_path.startswith(self.path):
            file_path = os.path.join(self.root, request_path.removeprefix(self.path))
            if file_path in self.filelist:
                file_to_serve = file_path

        if file_to_serve:
            stat_result = self.filelist[file_to_serve]
            return file_to_serve, stat_result

        return None

    async def __call__(self, scope, receive, send):
        try:
            await super().__call__(scope, receive, send)
        except HTTPNotFoundException:
            if scope["path"] == "/":
                new_scope = scope | {"path": f"{self.path}index.html"}
                await super().__call__(new_scope, receive, send)
            else:
                raise
