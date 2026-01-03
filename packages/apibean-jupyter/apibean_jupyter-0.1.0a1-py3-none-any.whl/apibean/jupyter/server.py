from __future__ import annotations

import threading
from typing import Optional

from jupyter_server.serverapp import ServerApp

from .plugins import JupyterPlugin


class JupyterServer:
    def __init__(
        self,
        *,
        root_dir: Optional[str] = None,
        ip: str = "127.0.0.1",
        port: Optional[int] = None,
        token: Optional[str] = None,
        lab: bool = True,
        extra_args: Optional[list[str]] = None,
        plugins: Optional[list[JupyterPlugin]] = None,
    ):
        self._plugins = plugins or []
        self._thread: Optional[threading.Thread] = None

        argv: list[str] = []

        if root_dir:
            argv += ["--ServerApp.root_dir", root_dir]
        if ip:
            argv += ["--ServerApp.ip", ip]
        if port:
            argv += ["--ServerApp.port", str(port)]
        if token is not None:
            argv += ["--ServerApp.token", token]

        if lab:
            argv.append("--ServerApp.default_url=/lab")

        if extra_args:
            argv += extra_args

        for p in self._plugins:
            p.pre_initialize({"argv": argv})

        self.app = ServerApp.instance()
        self.app.initialize(argv)

        for p in self._plugins:
            p.post_initialize(self.app)

    # - lifecycle -------------------------------

    def start(self, *, blocking: bool = True) -> None:
        for p in self._plugins:
            p.pre_start(self.app)

        if blocking:
            self.app.start()
        else:
            self._thread = threading.Thread(
                target=self.app.start,
                name="JupyterServerThread",
                daemon=True,
            )
            self._thread.start()

        for p in self._plugins:
            p.post_start(self.app)

    def stop(self) -> None:
        if self.app.io_loop:
            self.app.io_loop.stop()

        for p in self._plugins:
            p.shutdown(self.app)

    def is_running(self) -> bool:
        return self.app.io_loop is not None

    # - info ------------------------------------

    @property
    def url(self) -> str:
        return f"{self.app.connection_url}lab/?token={self.app.token}"

    @property
    def info(self) -> dict:
        return {
            "ip": self.app.ip,
            "port": self.app.port,
            "token": self.app.token,
            "base_url": self.app.base_url,
            "connection_url": self.app.connection_url,
            "display_url": self.app.display_url,
            "root_dir": self.app.root_dir,
            "pid": self.app.pid,
            "version": self.app.version,
        }
