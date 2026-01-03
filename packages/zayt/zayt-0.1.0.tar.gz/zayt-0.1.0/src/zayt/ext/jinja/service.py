import os
from http import HTTPStatus
from pathlib import Path
from typing import Annotated, Any

from asgikit import Request
from jinja2 import Environment, FileSystemLoader

from zayt.conf import Settings
from zayt.di.decorator import service
from zayt.di.inject import Inject


@service
def jinja_environment(settings: Settings) -> Environment:
    jinja_settings = settings.jinja

    kwargs: dict[str, Any] = dict(jinja_settings)

    if loader_settings := jinja_settings.get("loader"):
        if isinstance(loader_settings, Settings):
            loader_settings = dict(loader_settings)

            if "searchpath" not in loader_settings:
                loader_settings["searchpath"] = [
                    Path(os.getcwd()) / "resources" / "templates"
                ]

            if not isinstance(loader_settings["searchpath"], list):
                loader_settings["searchpath"] = [loader_settings["searchpath"]]

            kwargs["loader"] = FileSystemLoader(**loader_settings)
    else:
        kwargs["loader"] = FileSystemLoader(
            searchpath=Path(os.getcwd()) / "resources" / "templates"
        )

    kwargs.pop("enable_async", None)

    return Environment(enable_async=True, **kwargs)


@service
class JinjaTemplate:
    environment: Annotated[Environment, Inject]

    async def render(
        self,
        template_name: str,
        context: dict,
    ):
        template = self.environment.get_template(template_name)
        return await template.render_async(context)

    # pylint: disable=too-many-arguments
    async def respond(
        self,
        request: Request,
        template_name: str,
        context: dict,
        *,
        status=HTTPStatus.OK,
        media_type="text/html",
        stream: bool = False,
    ):
        template = self.environment.get_template(template_name)

        if stream:
            render_stream = template.generate_async(context)
            await request.respond_stream(
                (i.encode() async for i in render_stream),
                status=status,
                media_type=media_type,
            )
        else:
            rendered = await template.render_async(context)
            await request.respond_text(
                rendered,
                status=status,
                media_type=media_type,
            )
