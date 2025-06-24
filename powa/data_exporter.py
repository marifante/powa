from aiohttp import web
from typing import Union
import asyncio
import logging

from powa.async_task import AsyncTask
from powa.types import electrical_data


logger = logging.getLogger(__name__)


class DataExporter(AsyncTask):
    def __init__(self, *args, queues, ip:str = 'localhost', port:int = 8080, **kwargs):
        """ Data exporter constructor.

        :param queues: the dictionary with the queues where the exporter will read the data from.
        :param ip: the IP address to bind the HTTP server to.
        :param port: the port to bind the HTTP server to.
        """
        super().__init__(*args, **kwargs)

        self._queues = queues
        self._ip = ip
        self._port = port

        self._app = None
        self._runner = None
        self._site = None

    def _read_electrical_data(self, power_domain: str) -> Union[electrical_data, None]:
        """ Read electrical data for a specific power domain.

        :param power_domain: the power domain to read data from.
        :return: electrical_data object containing the data or None if no new data is available.
        """
        data = None

        try:
            data = self._queues[power_domain].get_nowait()
        except asyncio.QueueEmpty:
            logger.warning(f"No data available for power domain {power_domain}.")

        return data

    async def electrical_handler(self, request):
        """ Handle requests for electrical data.

        This handler will check if the requested power domain exists.
        If it does, it will return the latest electrical data for that domain.
        If there isn't any new data available, it will return a 204 No content response.
        If the power domain does not exist, it will return a 404 Not found response.

        :param request: the HTTP request object.
        :return: web.Response with the electrical data or an error message.
        """
        response = None
        data = None
        power_domain = request.match_info.get('power_domain', "?")

        if power_domain not in self._queues:
            response = web.Response(text=f"Power domain '{power_domain}' not found.", status=404)
        else:
            data = self._read_electrical_data(power_domain)
            if data is None:
                response = web.Response(text=f"No new data available for power domain '{power_domain}'.", status=204)
            else:
                data = {
                    'time': data.time,
                    'current': data.current,
                    'voltage': data.voltage,
                    'power': data.power
                }

                response = web.json_response(data, status=200)

        return response

    async def _handle_cancelled(self) -> None:
        """ Handle the cancellation of the async task. """
        if self._runner is not None:
            await self._runner.cleanup()
            logger.info("HTTP server runner cleaned up.")

    async def _async_task(self) -> None:
        """ Start the HTTP server to export data. """
        self._app = web.Application()
        self._app.router.add_get('/{power_domain}/electrical', self.electrical_handler)

        self._runner = web.AppRunner(self._app)
        await self._runner.setup()

        self._site = web.TCPSite(self._runner, self._ip, self._port)
        await self._site.start()

        while True:
            await asyncio.sleep(3600) # sleep forever
