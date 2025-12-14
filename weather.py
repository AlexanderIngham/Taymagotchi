import asyncio
import time
from dataclasses import dataclass
import python_weather


@dataclass
class Weather:
    temp_c: float
    condition: str
    icon_key: str  # one of: clear, clouds, rain, snow, mist


class PythonWeatherProvider:
    """Fetches current weather using the python-weather 2.x API."""
    def __init__(self, location="Halifax,CA", units="metric"):
        self.location = location
        self.units = units
        self._cache = None
        self._cache_ts = 0
        self._ttl = 600  # 10 minutes

    async def get_async(self) -> Weather:
        now = time.time()
        if self._cache and now - self._cache_ts < self._ttl:
            return self._cache

        # Create a client context for each call (python-weather 2.x)
        async with python_weather.Client(unit=python_weather.METRIC) as client:
            forecast = await client.get(self.location)

            # python-weather 2.x now uses .temperature and .description directly
            try:
                temp = forecast.temperature  # Current temperature in °C
                condition = forecast.description or "N/A"
            except AttributeError:
                # If older version, fallback to forecast.current
                temp = getattr(getattr(forecast, "current", None), "temperature", 0)
                condition = getattr(getattr(forecast, "current", None), "description", "N/A")

            icon_key = self._map_icon(condition)
            self._cache = Weather(temp, condition, icon_key)
            self._cache_ts = now
            return self._cache

    def get(self) -> Weather:
        """Synchronous wrapper for legacy compatibility."""
        return asyncio.run(self.get_async())

    @staticmethod
    def _map_icon(main: str) -> str:
        m = main.lower()
        if "rain" in m:
            return "rain"
        if "snow" in m:
            return "snow"
        if "cloud" in m:
            return "clouds"
        if "mist" in m or "fog" in m or "haze" in m:
            return "mist"
        return "clear"


def load_provider():
    """Default provider for app.py"""
    return PythonWeatherProvider()
