from __future__ import annotations

import dataclasses
import socket
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncContextManager,
    Callable,
    Mapping,
    Optional,
    Protocol,
    TypeVar,
)

from structlog import BoundLogger

if TYPE_CHECKING:
    from aio.future import Coroutine

T = TypeVar('T')
CallbackType = Callable[..., None]


class Clock:
    def now(self) -> float:
        raise NotImplementedError

    def resolution(self) -> float:
        raise NotImplementedError


class EventCallback(Protocol):
    def __call__(self, fd: int, events: int) -> None:
        raise NotImplementedError


class EventSelector(Protocol):
    def select(self, time_: Optional[float]) -> None:
        raise NotImplementedError

    def add_watch(self, fd: int, events: int, cb: EventCallback) -> None:
        raise NotImplementedError

    def stop_watch(self, fd: int, events: Optional[int], cb: Optional[EventCallback]) -> None:
        raise NotImplementedError

    def wakeup_thread_safe(self) -> None:
        raise NotImplementedError

    def finalize(self) -> None:
        raise NotImplementedError


@dataclasses.dataclass
class Handle:
    when: Optional[float]
    callback: CallbackType
    args: tuple[Any] = ()
    cancelled: bool = False
    context: Mapping[str, Any] = dataclasses.field(default_factory=dict)

    def cancel(self):
        self.cancelled = True


class UnhandledExceptionHandler(Protocol):
    def __call__(self, exc: Exception, logger_: BoundLogger, /, **context: Any) -> None:
        raise NotImplementedError


class EventLoop(Protocol):
    def call_soon(
        self,
        target: CallbackType,
        *args: Any,
        context: Optional[Mapping[str, Any]] = None,
    ) -> Handle:
        raise NotImplementedError

    def call_later(
        self,
        timeout: float,
        target: CallbackType,
        *args: Any,
        context: Optional[Mapping[str, Any]] = None,
    ) -> Handle:
        raise NotImplementedError

    @property
    def clock(self) -> Clock:
        raise NotImplementedError

    def create_networking(self) -> AsyncContextManager[Networking]:
        raise NotImplementedError


class LoopRunner(Protocol):
    @property
    def loop(self) -> EventLoop:
        raise NotImplementedError

    def run_coroutine(self, coroutine: Coroutine[T]) -> T:
        raise NotImplementedError


class LoopFactory(Protocol):
    def __call__(self, **loop_kwargs: Any) -> tuple[LoopRunner, EventLoop]:
        raise NotImplementedError


class Networking(Protocol):
    async def wait_sock_ready_to_read(self, sock: socket.socket) -> None:
        """

        :param sock:
        :return:
        :raises SocketMustBeNonBlockingError: if given socket not in non-blocking mode
        """
        raise NotImplementedError

    async def wait_sock_ready_to_write(self, sock: socket.socket) -> None:
        """

        :param sock:
        :return:
        :raises SocketMustBeNonBlockingError: if given socket not in non-blocking mode
        """
        raise NotImplementedError

    async def sock_connect(self, sock: socket.socket, addr: Any) -> None:
        """

        :param sock:
        :param addr:
        :return:
        :raises SocketMustBeNonBlockingError: if given socket not in non-blocking mode
        """
        raise NotImplementedError

    async def sock_accept(self, sock: socket.socket) -> tuple[socket.socket, Any]:
        """

        :param sock:
        :return:
        :raises SocketMustBeNonBlockingError: if given socket not in non-blocking mode
        """
        raise NotImplementedError

    async def sock_read(self, sock: socket.socket, amount: int) -> bytes:
        """

        :param sock:
        :param amount:
        :return:
        :raises SocketMustBeNonBlockingError: if given socket not in non-blocking mode
        """
        raise NotImplementedError

    async def sock_write(self, sock: socket.socket, data: bytes) -> None:
        """

        :param sock:
        :param data:
        :return:
        :raises SocketMustBeNonBlockingError: if given socket not in non-blocking mode
        """
        raise NotImplementedError
