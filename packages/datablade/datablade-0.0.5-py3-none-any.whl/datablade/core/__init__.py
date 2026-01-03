"""Backward-compatible exports for the legacy datablade.core namespace.

Historically, this package used dynamic imports to re-export everything.
We keep the same runtime surface area but use explicit imports so that IDEs,
type checkers, and static analysis tools can reason about the module.
"""

from . import frames as _frames
from . import json as _json
from . import lists as _lists
from . import messages as _messages
from . import strings as _strings
from . import zip as _zip
from .frames import *  # noqa: F401,F403
from .json import *  # noqa: F401,F403
from .lists import *  # noqa: F401,F403
from .messages import *  # noqa: F401,F403
from .strings import *  # noqa: F401,F403
from .zip import *  # noqa: F401,F403

__all__ = [
    *_frames.__all__,
    *_json.__all__,
    *_lists.__all__,
    *_messages.__all__,
    *_strings.__all__,
    *_zip.__all__,
]
