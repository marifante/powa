from typing import Dict
import asyncio
import time

from powa.async_task import AsyncTask
from powa.types import electrical_data
from powa.ina260 import Ina260 as PowerSensor


class PDController(AsyncTask):
    def __init__(self, *args, **kwargs):
        """ Power Domain Controller constructor.

        :param queue: the queue where the PD controller will put the electrical data of the power domain.
        """
        super().__init__(*args, **kwargs)

        self._queue = kwargs.get('queue')

        self._current_sensor = PowerSensor()
        self._polling_interval_s = self._config.get('polling_interval', 1.0)

    def _configure_sensor(self) -> None:
        """ Configure the INA260 sensor with the settings from the configuration. """
        raise NotImplementedError("Not implenmented yet.")

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

