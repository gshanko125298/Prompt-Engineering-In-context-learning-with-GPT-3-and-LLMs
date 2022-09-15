from .private import private
from .public import public


__version__ = '3.1.1'


def install() -> None:
    """Install @public and @private into builtins."""
    import builtins

    builtins.public = public            # type: ignore [attr-defined]
    builtins.private = private          # type: ignore [attr-defined]


# mypy does not understand that __all__ gets populated at runtime via the
# following call,
__all__ = [
    'private',
    'public',
]


public(
    private=private,
    public=public,
)
