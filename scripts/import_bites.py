import asyncio

import pandas as pd

from db.database import async_session_maker
from repositories.bite_repo import create_bite


async def main():
    df = pd.read_excel("../data/ticks_dataset_test.xlsx")

    df = df.drop(columns=["n", "id"], errors="ignore")
    df = df.dropna(subset=['X_bite', 'Y_bite'])

    df["X_bite"] = df["X_bite"].astype(str).str.replace(",", ".").astype(float)
    df["Y_bite"] = df["Y_bite"].astype(str).str.replace(",", ".").astype(float)

    async with async_session_maker() as session:
        for _, row in df.iterrows():

            point_wkt = f"POINT({row.X_bite} {row.Y_bite})"

            try:
                await create_bite(
                    session,
                    date_of_bite=row.date,
                    point_wkt=point_wkt,
                    location_description=row.location,
                )
            except Exception as e:
                print(f"Ошибка в записи: {_}: {e}")

    print("Перенос завершён")


if __name__ == "__main__":
    asyncio.run(main())
