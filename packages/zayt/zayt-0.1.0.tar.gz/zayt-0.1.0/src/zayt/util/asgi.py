from collections.abc import Iterator


def get_header(header_name: str, scope: dict, default=None) -> str | None:
    """Retrieve the header value from the asgi scope

    :return: The decoded header value or the given default
    :raises ValueError: If the scope does not have the "headers" key
    """

    return next(get_header_all(header_name, scope), default)


def get_header_all(header_name: str, scope: dict) -> Iterator[str]:
    """Iterate over all header values for the given header name in the asgi scope

    :return: And iterator over the decoded header values
    :raises ValueError: If the scope does not have the "headers" key
    """

    if "headers" not in scope:
        raise ValueError("invalid scope")

    for name, value in scope["headers"]:
        if name.decode("ascii").lower() == header_name:
            yield value.decode("ascii")
