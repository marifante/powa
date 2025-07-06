import logging
import asyncio
from typing import Any, Optional
from types import FrameType
import os
import signal

from powa.pd_control import DefaultConfig, PDController
from powa.data_exporter import DataExporter
from powa.types import PowerDomain
from powa.utils import parse_yaml_file


logger = logging.getLogger(__name__)


DAEMON_LOCK_FILE = "/var/run/powa_daemon.lock"


class PowaDaemon:
    def __init__(self, config: str):
        """ Initialize powa daemon object.

        The daemon will create 1 task for each power domain
        and another one for the data exporter (http server).

        :param config: path to the yml configuration file.
        """
        self._config_file = config

        self._pid = os.getpid()
        self._lock_file = DAEMON_LOCK_FILE

        self._config = parse_yaml_file(self._config_file)

        # A pd controller task will be created for each power domain,
        # even though one of them may not be configured, it should use a default configuration.
        self._queues = {domain.value: asyncio.Queue() for domain in PowerDomain}
        self._pds_tasks = tuple(
            PDController(config=self._config if self._config.get('power_domain', {}).get(domain.value, None) else DefaultConfig.to_dict(),
                         name=domain.value,
                         queue=self._queues[domain.value]).task
            for domain in PowerDomain
        )

        self._tasks = self._pds_tasks + (DataExporter(self._config, self._queues).task, )

        signal.signal(signal.SIGTERM, self._handle_sigterm)

    def _create_lock_file(self) -> None:
        """ Create a lock file to prevent multiple instances of the daemon from running simultaneously.

        This method creates a lock file at the specified path. If the file already exists, it raises an exception.
        """
        if os.path.exists(self._lock_file):
            raise FileExistsError(f"Daemon lock file {DAEMON_LOCK_FILE} already exists. Another instance may be running.")

        with open(self._lock_file, 'w') as f:
            f.write(str(self._pid))

        logger.info(f"Lock file created at {DAEMON_LOCK_FILE} for pid {self._pid}")

    def _handle_sigterm(self, signum: int, frame: Optional[FrameType]) -> None:
        """ Handle SIGTERM signal to gracefully stop the daemon.

        This method is called when the daemon receives a SIGTERM signal.
        It cleans up resources and stops the daemon.

        :param signum: the signal number that was received.
        :param frame: the current stack frame (not used).
        """
        logger.info(f"Received SIGTERM signal (signal number: {signum}). Stopping daemon with pid {self._pid}")

        if os.path.exists(self._lock_file):
            os.remove(self._lock_file)
            logger.info(f"Lock file {self._lock_file} removed.")
        else:
            logger.warning(f"Lock file {self._lock_file} does not exist. Nothing to remove.")

        # Here you can add any additional cleanup code if needed
        for task in self._tasks:
            if task is not None and not task.done():
                task.cancel()
                logger.info(f"Cancelled task {task}")

        logger.info(f"Daemon on pid = {self._pid} stopped gracefully.")

    async def start(self):
        """ Start the powa daemon, which involves starting the correspondent asyncio tasks. """
        logger.info(f"Starting daemon on pid = {self._pid}")

        self._create_lock_file()

        if any(x is None for x in self._tasks):
            await asyncio.gather(*self._tasks)

    def __enter__(self):
        """ Context manager enter method to start the daemon. """
        logger.info("Entering PowaDaemon context manager.")
        return self

    def __exit__(self, exc_type: Optional[type], exc_value: Optional[BaseException], traceback: Optional[Any]) -> None:
        """ Context manager exit method to stop the daemon and clean up resources.

        :param exc_type: the type of the exception raised, if any.
        :param exc_value: the value of the exception raised, if any.
        :param traceback: the traceback object, if any.
        """
        logger.info("Exiting PowaDaemon context manager.")

        if os.path.exists(DAEMON_LOCK_FILE):
            os.remove(DAEMON_LOCK_FILE)
            logger.info(f"Erased lock file located in {DAEMON_LOCK_FILE}.")


def start_daemon(config: str) -> None:
    """ Start the powa daemon by creating an instance of PowaDaemon and calling its start method.

    :param config: path to the yml configuration file.
    """
    with PowaDaemon(config=config) as daemon:
        asyncio.run(daemon.start())


def stop_daemon() -> None:
    """ Stop the powa deaemon by sending a SIGTERM signal to the process. """
    pid = None
    if not os.path.exists(DAEMON_LOCK_FILE):
        raise RuntimeError(f"Daemon lock file {DAEMON_LOCK_FILE} does not exist. Daemon is not running probably.")

    with open(DAEMON_LOCK_FILE, 'r') as f:
        pid = int(f.read().strip())

    logger.info(f"Sending a SIGTERM signal to the daemon (pid = {pid}) from process with pid = {os.getpid()}")
