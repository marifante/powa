import asyncio
from typing import Coroutine, Dict
import logging

logger = logging.getLogger(__name__)


class AsyncTask:
    """ Base class for asynchronous tasks. """
    def __init__(self, config: Dict):
        """ Async task constructor.

        :param config: a dictionary containing the configuration of this task.
        """
        self._config = config

    async def _async_task(self) -> None:
        """ Coroutine task. """
        raise NotImplementedError("This should be implemented by the child class, not the base class.")

    async def _handle_cancelled(self) -> None:
        """ Handler used to do any kind of cleanup the async task needs in a cancel event. """
        raise NotImplementedError("This should be implemented by the child class, not the base class.")

    async def _safe_async_task(self) -> None:
        """ Safely run the async task.

        This method is used to ensure that the async task is run in a safe manner,
        handling any exceptions that may occur during its execution.
        """
        try:
            await self._async_task()
        except asyncio.CancelledError as e:
            await self._handle_cancelled()
        except Exception as e:
            logger.error(f"An error occurred during task execution: {e}")

    @property
    def task(self) -> Coroutine:
        """ Returns the coroutine task for this async task. """
        return self._safe_async_task()
