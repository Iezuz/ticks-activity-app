import httpx
import logging
from datetime import date, timedelta
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class OpenMeteoService:

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10)
        self._cache = {}

    async def get_batch_weather(
        self,
        points: List[Tuple[float, float, date]]
    ) -> Dict[Tuple[float, float, date], dict]:

        result = {}
        today = date.today()

        archive_points = []
        forecast_points = []
        fallback_points = []

        print(f"[WEATHER] incoming points: {len(points)}")

        for lat, lon, d in points:
            key = (round(lat, 3), round(lon, 3), d)

            if key in self._cache:
                result[key] = self._cache[key]
                continue

            if d <= today:
                archive_points.append((lat, lon, d))
            elif d <= today + timedelta(days=16):
                forecast_points.append((lat, lon, d))
            else:
                fallback_points.append((lat, lon, d))

        print(
            f"[WEATHER] split → archive={len(archive_points)}, "
            f"forecast={len(forecast_points)}, fallback={len(fallback_points)}"
        )

        if archive_points:
            result.update(await self._fetch_archive_batch(archive_points))

        if forecast_points:
            result.update(await self._fetch_forecast_batch(forecast_points))

        for lat, lon, d in fallback_points:
            key = (round(lat, 3), round(lon, 3), d)

            logger.warning(f"[WEATHER][FALLBACK] {lat},{lon} {d}")

            value = {"cloudiness": None, "precipitation": None}
            self._cache[key] = value
            result[key] = value

        return result

    # ==========================================================
    # ARCHIVE
    # ==========================================================

    async def _fetch_archive_batch(self, points):

        result = {}

        grouped = {}
        for lat, lon, d in points:
            grouped.setdefault(d, []).append((lat, lon, d))

        for d, group_points in grouped.items():

            print(f"[ARCHIVE] date={d}, points={len(group_points)}")

            lats = ",".join(str(p[0]) for p in group_points)
            lons = ",".join(str(p[1]) for p in group_points)

            params = {
                "latitude": lats,
                "longitude": lons,
                "hourly": "cloudcover",
                "daily": "precipitation_sum",
                "start_date": d.isoformat(),
                "end_date": d.isoformat(),
                "timezone": "UTC"
            }

            try:
                resp = await self.client.get(ARCHIVE_URL, params=params)
                print(f"[ARCHIVE] status={resp.status_code}")
                data = resp.json()
            except Exception as e:
                logger.error(f"[ARCHIVE][ERROR] {e}")
                data = []

            if isinstance(data, dict):
                data = [data]

            for i, (lat, lon, d) in enumerate(group_points):
                key = (round(lat, 3), round(lon, 3), d)

                item = data[i] if i < len(data) else {}

                value = self._parse_weather(item)

                if value["cloudiness"] is None:
                    logger.warning(f"[ARCHIVE][NO CLOUD] {lat},{lon} {d}")

                if value["precipitation"] is None:
                    logger.warning(f"[ARCHIVE][NO PRECIP] {lat},{lon} {d}")

                self._cache[key] = value
                result[key] = value

        return result

    # ==========================================================
    # FORECAST
    # ==========================================================

    async def _fetch_forecast_batch(self, points):

        result = {}

        grouped = {}
        for lat, lon, d in points:
            grouped.setdefault(d, []).append((lat, lon, d))

        for d, group_points in grouped.items():

            print(f"[FORECAST] date={d}, points={len(group_points)}")

            lats = ",".join(str(p[0]) for p in group_points)
            lons = ",".join(str(p[1]) for p in group_points)

            params = {
                "latitude": lats,
                "longitude": lons,
                "hourly": "cloudcover",
                "daily": "precipitation_sum",
                "timezone": "UTC"
            }

            try:
                resp = await self.client.get(FORECAST_URL, params=params)
                print(f"[FORECAST] status={resp.status_code}")
                data = resp.json()
            except Exception as e:
                logger.error(f"[FORECAST][ERROR] {e}")
                data = []

            if isinstance(data, dict):
                data = [data]

            for i, (lat, lon, d) in enumerate(group_points):
                key = (round(lat, 3), round(lon, 3), d)

                item = data[i] if i < len(data) else {}

                value = self._parse_forecast_day(item, d)

                if value["cloudiness"] is None:
                    logger.warning(f"[FORECAST][NO CLOUD] {lat},{lon} {d}")

                if value["precipitation"] is None:
                    logger.warning(f"[FORECAST][NO PRECIP] {lat},{lon} {d}")

                self._cache[key] = value
                result[key] = value

        return result

    # ==========================================================
    # PARSING
    # ==========================================================

    def _parse_weather(self, item):

        daily = item.get("daily", {})
        hourly = item.get("hourly", {})

        precip = None
        if "precipitation_sum" in daily:
            vals = daily["precipitation_sum"]
            if vals:
                precip = float(vals[0])

        cloud = None
        if "cloudcover" in hourly:
            vals = hourly["cloudcover"]
            if vals:
                cloud = float(sum(vals) / len(vals))

        return {
            "cloudiness": cloud,
            "precipitation": precip
        }

    def _parse_forecast_day(self, item, target_date):

        daily = item.get("daily", {})
        hourly = item.get("hourly", {})

        precip = None
        cloud = None

        if "time" in daily:
            try:
                idx = daily["time"].index(target_date.isoformat())
                precip = float(daily["precipitation_sum"][idx])
            except Exception:
                pass

        if "time" in hourly:
            vals = [
                c for t, c in zip(hourly["time"], hourly["cloudcover"])
                if t.startswith(target_date.isoformat())
            ]
            if vals:
                cloud = float(sum(vals) / len(vals))

        return {
            "cloudiness": cloud,
            "precipitation": precip
        }

    #print(f"cloud={cloud}, precip={precip}, lat={lat}, lon={lon}, date={d}")
    #daily = data[i].get("daily", {})
    #hourly = data[i].get("hourly", {})
    #print(ф)