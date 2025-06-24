import logging
import asyncio
from typing import Any, Optional
from types import FrameType
import yaml
import os
import signal

from powa.pd_control import PDController
from powa.data_exporter import DataExporter
from powa.types import PowerDomain


logger = logging.getLogger(__name__)


DAEMON_LOCK_FILE = "/var/run/powa_daemon.lock"


def parse_yaml_file(file_path) -> Any:
    """ Load the information of a yaml file.

    :param file_path: the path to the yaml file.
    :return: the content of the yaml file.
    """
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


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

        self._queues = {domain.value: asyncio.Queue() for domain in PowerDomain}
        self._pds_tasks = tuple(
            PDController(name=domain.value,
                         config=self._config,
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


def start_daemon(config: str) -> None:
    """ Start the powa daemon by creating an instance of PowaDaemon and calling its start method.

    :param config: path to the yml configuration file.
    """
    asyncio.run(PowaDaemon(config=config).start())
    logger.info("Powa daemon started successfully.")


def stop_daemon() -> None:
    """ Stop the powa deaemon by sending a SIGTERM signal to the process. """
    pid = None
    if not os.path.exists(DAEMON_LOCK_FILE):
        raise RuntimeError(f"Daemon lock file {DAEMON_LOCK_FILE} does not exist. Daemon is not running probably.")

    with open(DAEMON_LOCK_FILE, 'r') as f:
        pid = int(f.read().strip())

    logger.info(f"Sending a SIGTERM signal to the daemon (pid = {pid}) from process with pid = {os.getpid()}")
