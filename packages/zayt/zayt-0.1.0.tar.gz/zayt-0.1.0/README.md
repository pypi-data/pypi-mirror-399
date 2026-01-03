# Project Zayt

Zayt is a Python ASGI web framework built on top of [asgikit](https://pypi.org/project/asgikit/)
and inspired by Spring Boot, AspNet, FastAPI and Go's net/http.

It features a Dependency Injection system to help build robust and reliable applications.

## Quick start

Install `zayt` and `uvicorn` to run application:

```shell
pip install zayt uvicorn[standard]
```

Create a module called `application.py`:

```shell
touch application.py
```

Create a handler:

```python
from asgikit import Request
from zayt.web import get


@get
async def hello(request: Request):
    await request.respond_text("Hello, World!")
```

Run application with `uvicorn` (Zayt will automatically load `application.py`):

```shell
uvicorn zayt.run:app --reload
```
