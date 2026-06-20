import httpx
from datetime import date
from typing import List, Dict


class ForecastApiService:

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10)

    async def get_one_week_forecast(self, lat: float, lon: float) -> List[Dict]:

        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_mean,snow_depth",
            "forecast_days": 7,
            "timezone": "auto",
        }

        r = await self.client.get(self.BASE_URL, params=params)
        r.raise_for_status()

        data = r.json()["daily"]

        result = []
        for i in range(len(data["time"])):
            result.append({
                "date": date.fromisoformat(data["time"][i]),
                "temperature": data["temperature_2m_mean"][i],
                "snow_depth": data.get("snow_depth", [None]*7)[i],
            })

        return result
