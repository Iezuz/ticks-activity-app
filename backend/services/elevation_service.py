import httpx
from typing import List, Dict, Tuple


class ElevationService:
    BASE_URL = "https://api.open-elevation.com/api/v1/lookup"

    async def get_bulk_elevations(self, coordinates: List[Tuple[float, float]]) -> Dict[Tuple[float, float], float]:

        results = {}
        batch_size = 100

        async with httpx.AsyncClient(timeout=50) as client:

            for i in range(0, len(coordinates), batch_size):

                batch = coordinates[i:i + batch_size]

                payload = {"locations": [{"latitude": lat, "longitude": lon} for lat, lon in batch]}

                response = await client.post(self.BASE_URL, json=payload)
                response.raise_for_status()

                data = response.json()["results"]

                for coord, item in zip(batch, data):
                    results[coord] = item["elevation"]

        return results
