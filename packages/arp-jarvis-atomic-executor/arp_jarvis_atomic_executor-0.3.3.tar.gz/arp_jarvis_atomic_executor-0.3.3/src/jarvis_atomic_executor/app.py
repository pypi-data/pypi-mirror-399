from __future__ import annotations

from .executor import AtomicExecutor
from .utils import auth_settings_from_env_or_dev_secure


def create_app():
    return AtomicExecutor().create_app(
        title="JARVIS Atomic Executor",
        auth_settings=auth_settings_from_env_or_dev_secure(),
    )


app = create_app()
