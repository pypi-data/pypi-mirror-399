from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dojo_sdk_core.dojos.dojos_loader import collect_tasks, load_dojos
    from dojo_sdk_core.dojos.model import Dojo

__all__ = ["Dojo", "collect_tasks", "load_dojos"]


def __getattr__(name: str):
    if name in {"collect_tasks", "load_dojos"}:
        from dojo_sdk_core.dojos import dojos_loader

        return getattr(dojos_loader, name)
    if name == "Dojo":
        from dojo_sdk_core.dojos.model import Dojo

        return Dojo
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
