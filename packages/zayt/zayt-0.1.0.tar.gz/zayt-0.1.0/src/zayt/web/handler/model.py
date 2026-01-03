from typing import NamedTuple

from zayt.di.inject import Inject


class RequestParam(NamedTuple):
    param_type: type
    param_meta: Inject | None
    has_default: bool
