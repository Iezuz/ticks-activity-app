from backend.repositories.forecast_generation_repo import create_future_cluster_data

from backend.services.forecast_weather_service import ForecastWeatherService

from backend.services.prediction_service import PredictionService


class PredictionPipelineService:

    def __init__(self, db):
        self.db = db

    async def run(self):

        await create_future_cluster_data(self.db)

        weather_service = ForecastWeatherService(self.db)

        await weather_service.fill_forecast_weather()

        short_service = PredictionService(self.db)
        await short_service.predict_short()

        long_service = PredictionService(self.db)
        await long_service.predict_long()
