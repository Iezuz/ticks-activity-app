from enum import Enum


class WeatherStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    NO_STATION = "FAILED"
    NO_DATA = "NO DATA"
    NO_DATE = "NO DATE"
    NO_SNOW = "NO SNOW"
    NO_TEMP = "NO TEMP"
    ERROR = "ERROR"
