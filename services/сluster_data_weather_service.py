from typing import List

import pandas as pd
from geoalchemy2.shape import to_shape
from meteostat import Point, daily, stations
from shapely import wkt
from enums.bite_status_enum import WeatherStatus


class ClusterDataWeatherService:
    def __init__(self):
        self._station_cache = {}

    async def get_weather_data_by_coors(self, cluster_data_list: List):
        """
        Для каждой записи ClusterData получает температуру и глубину снега
        по центроиду кластера и дате, обновляет status
        """

        unique_coors = set()
        data_map = {}
        cntr = 0
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        for cd in cluster_data_list:
            cntr += 1
            centroid = wkt.loads(cd.cluster.centroid_wkt)
            lat, lon = centroid.y, centroid.x
            unique_coors.add((lat, lon))
            data_map[cd.id] = {"cd": cd, "lat": lat, "lon": lon}

            station_id = self._get_nearest_station(lat, lon)
            if not station_id:
                print("Для этого среза нет станции")
                cd.weather_status = WeatherStatus.NO_STATION
                continue
            print("passed station")
            df = daily(station_id, cd.date, cd.date).fetch()
            if df is None or df.empty:
                print("Для этого среза нет данных")
                cd.weather_status = WeatherStatus.NO_DATA
                continue
            print("passed daily")
            df.index = df.index.date
            if cd.date not in df.index:
                print("У этого среза нет даты")
                cd.weather_status = WeatherStatus.NO_DATE
                continue
            print("passed date")
            row = df.loc[cd.date]
            temp_value = row.get("temp")
            snow_value = row.get("snwd")
            print("passed row get")
            has_temp = pd.notna(temp_value)
            has_snow = pd.notna(snow_value)
            print("passed notna")
            cd.temperature = float(temp_value) if has_temp else None
            cd.avg_snow_depth = float(snow_value) if has_snow else None
            print("passed floating")
            if has_temp and has_snow:
                cd.weather_status = WeatherStatus.SUCCESS
                print('success')
            elif has_temp and not has_snow:
                cd.weather_status = WeatherStatus.NO_SNOW
                cd.weather_status = WeatherStatus.NO_SNOW
                print('no_snow')
            elif has_snow and not has_temp:
                cd.weather_status = WeatherStatus.NO_TEMP
                print('no_temp')
            else:
                cd.weather_status = WeatherStatus.NO_DATA
                print('no_data')
            print("passed status")

    def _get_nearest_station(self, lat: float, lon: float):
        key = (round(lat, 3), round(lon, 3))
        if key in self._station_cache:
            return self._station_cache[key]

        station = stations.nearby(Point(lat, lon), limit=1, radius=500_000)
        if station.empty:
            return None

        station_id = station.index[0]
        self._station_cache[key] = station_id
        return station_id
