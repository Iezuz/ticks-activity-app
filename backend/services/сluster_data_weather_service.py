import pandas as pd
import numpy as np

from typing import List, Dict, Any
from datetime import timedelta

from meteostat import Point, daily, stations

from enums.bite_status_enum import WeatherStatus
from repositories.cluster_data_repo import bulk_update_cluster_data_weather
from services.open_meteo_service import OpenMeteoService
from collections import defaultdict


class ClusterDataWeatherService:
    def __init__(self):
        self._station_cache: Dict[tuple, List[str]] = {}
        self.open_meteo = OpenMeteoService()
        self._snow_cache: Dict[tuple, float | None] = {}
        self._meteostat_cache = {}

    async def process_batch(self, db, rows):

        def chunked(lst, size):
            for i in range(0, len(lst), size):
                yield lst[i:i + size]

        points = [(row.lat, row.lon, row.date) for row in rows]
        print(f"Получено {len(points)} записей из БД")
        meteo_data = {}

        for chunk in chunked(points, 100):
            chunk_result = await self.open_meteo.get_batch_weather(chunk)
            meteo_data.update(chunk_result)

        updates = []

        self._preload_meteostat(rows)

        for row in rows:
            lat = row.lat
            lon = row.lon
            date = row.date

            key = (round(lat, 3), round(lon, 3), date)
            print(f"Получение информации для {key}")
            meteostat_data = self._process_meteostat(lat, lon, date)
            snow_feature = self._compute_snow_feature(lat, lon)

            meteo = meteo_data.get(key, {
                "cloudiness": None,
                "precipitation": None
            })

            updates.append({
                "id": row.id,
                "temperature": meteostat_data["temperature"],
                "snow": snow_feature,
                "precipitation": meteo["precipitation"] or meteostat_data["precipitation"],
                "cloudiness": meteo["cloudiness"],
                "status": self._determine_status(meteostat_data["temperature"]),
            })
            print(f'обл в process_batch {meteo["cloudiness"]}')
        await bulk_update_cluster_data_weather(db, updates)

    def _preload_meteostat(self, rows):
        """
        Загружает данные Meteostat один раз на станцию
        """

        station_to_rows = defaultdict(list)

        for row in rows:
            lat, lon = row.lat, row.lon

            sts = self._get_nearest_stations(lat, lon)

            for st in sts:
                station_to_rows[st].append(row)

        for station_id, rows_list in station_to_rows.items():

            dates = [r.date for r in rows_list]
            start = min(dates) - timedelta(days=3)
            end = max(dates) + timedelta(days=3)

            key = (station_id, start, end)

            if key in self._meteostat_cache:
                continue

            try:
                df = daily(station_id, start, end).fetch()
            except Exception:
                continue

            if df is None or df.empty:
                print(f"Не удалось получить данные по {key}")
                continue

            df.index = df.index.date

            self._meteostat_cache[key] = df

    def _process_meteostat(self, lat, lon, date):

        station_ids = self._get_nearest_stations(lat, lon)

        if not station_ids:
            print(f"Не удалось получить станцию по координатам ({lat}, {lon}) для температуры и осадков")
            return self._empty(WeatherStatus.NO_STATION)

        temps = []
        precs = []

        for station_id in station_ids:

            for (st_id, start, end), df in self._meteostat_cache.items():
                if st_id != station_id:
                    continue

                for d in pd.date_range(date - timedelta(days=3), date + timedelta(days=3)).date:
                    if d not in df.index:
                        continue

                    row = df.loc[d]

                    t = row.get("tavg") or row.get("temp")
                    p = row.get("prcp")

                    if pd.notna(t):
                        temps.append(t)

                    if pd.notna(p):
                        precs.append(p)

        temperature = float(np.mean(temps)) if temps else None
        precipitation = float(np.mean(precs)) if precs else None
        print(f"!!!!!!!!!!!облачность - {precipitation}")
        status = self._determine_status(temperature)

        return {
            "temperature": temperature,
            "precipitation": precipitation,
            "status": status,
        }

    def _get_nearest_stations(self, lat: float, lon: float, limit: int = 5) -> List[str]:
        key = (round(lat, 3), round(lon, 3))

        if key in self._station_cache:
            return self._station_cache[key]

        sts = stations.nearby(Point(lat, lon), limit=limit)

        if sts.empty:
            self._station_cache[key] = []
            return []

        ids = sts.index.tolist()
        self._station_cache[key] = ids
        return ids

    def _compute_snow_feature(self, lat: float, lon: float) -> float | None:
        key = (round(lat, 2), round(lon, 2))

        if key in self._snow_cache:
            return self._snow_cache[key]

        station_ids = self._get_nearest_stations(lat, lon)

        if not station_ids:
            print(f"Не удалось получить станцию по координатам {key} для получения информации о глубине снега")
            self._snow_cache[key] = None
            return None

        from datetime import date
        end = date.today()
        start = date(end.year - 3, 1, 1)

        snow_values = []

        for station_id in station_ids:
            try:
                df = daily(station_id, start, end).fetch()
            except Exception:
                continue

            if df is None or df.empty:
                print(f"Отутствуют данные о погоде за период {start} - {end}")
                continue

            if "snwd" not in df.columns:
                print(f"Отутствует данные о глубине снега за период {start} - {end}")
                continue

            snwd = df["snwd"].dropna()

            snwd = snwd[snwd > 0]

            if not snwd.empty:
                snow_values.extend(snwd.tolist())

        result = float(np.mean(snow_values)) if snow_values else None

        self._snow_cache[key] = result
        return result

    def _determine_status(self, temp):
        if temp is not None:
            print("назначен статус SUCCESS")
            return WeatherStatus.SUCCESS

        print("назначен статус NO_DATA")
        return WeatherStatus.NO_DATA

    def _empty(self, status):
        return {
            "temperature": None,
            "snow": None,
            "precipitation": None,
            "status": status,
        }
