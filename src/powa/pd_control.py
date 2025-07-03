from typing import Dict
import asyncio
import time
from enum import Enum

from powa.async_task import AsyncTask
from powa.types import electrical_data
from powa.ina260 import Ina260 as PowerSensor


class DefaultConfig(Enum):
    """ Default configuration for the power domain controller. """
    POLLING_INTERVAL = 30.0  # Default polling interval in seconds

    @classmethod
    def to_dict(cls):
        """ Convert the enum to a dictionary representation. """
        return {item.name: item.value for item in cls}


class PDController(AsyncTask):
    def __init__(self, *args, name:str, queue: asyncio.Queue, **kwargs):
        """ Power Domain Controller constructor.

        :param queue: the queue where the PD controller will put the electrical data of the power domain.
        :param name: the name of the power domain.
        """
        super().__init__(*args, **kwargs)

        self._name = name
        self._queue = queue

        self._current_sensor = PowerSensor()

        self._config = kwargs.get('config', DefaultConfig.to_dict())

    def _configure_sensor(self) -> None:
        """ Configure the INA260 sensor with the settings from the configuration. """
        raise NotImplementedError("Not implemented yet.")

    async def _async_task(self) -> None:
        """ Create a coroutine task for the PD controller. """

        self._configure_sensor()

        while True:
            current = self._current_sensor.current
            voltage = self._current_sensor.voltage
            power = self._current_sensor.power

            self._queue.put(electrical_data(time=time.monotonic(),
                                            current=current,
                                            voltage=voltage,
                                            power=power))

            await asyncio.sleep(self._polling_interval_s)

