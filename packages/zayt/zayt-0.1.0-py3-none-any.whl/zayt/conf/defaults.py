default_settings = {
    "__application__": "application",
    "extensions": [],
    "asgi_middleware": [],
    "logging": {
        "setup": "zayt.logging:setup",
    },
    "jinja": {},
    "memcached": {},
    "redis": {},
    "sqlalchemy": {
        "connections": {},
        "session": {},
    },
    "staticfiles": {
        "path": "/static",
        "root": "resources/static",
        "mappings": {},
    },
    "uploadedfiles": {
        "path": "/uploads",
        "root": "resources/uploads",
    },
}
