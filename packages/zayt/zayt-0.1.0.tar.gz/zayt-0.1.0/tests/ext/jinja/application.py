from asgikit import Request

from zayt.ext.jinja import JinjaTemplate
from zayt.web import get


@get("/render")
async def render(request: Request, template: JinjaTemplate):
    await template.respond(request, "template.html", {"variable": "Jinja"})


@get("/stream")
async def stream(request: Request, template: JinjaTemplate):
    await template.respond(
        request,
        "template.html",
        {"variable": "Jinja"},
        stream=True,
    )


@get("/content_type")
async def content_type(request: Request, template: JinjaTemplate):
    await template.respond(
        request,
        "template.html",
        {"variable": "Jinja"},
        media_type="text/plain",
    )
