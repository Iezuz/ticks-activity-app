import asyncio
import pandas as pd

from sqlalchemy import text, bindparam
from sqlalchemy.types import Date, Float, String

from db.database import async_session_maker


async def main():
    df = pd.read_excel(
        "../data/ticks_dataset.xlsx",
        sheet_name=0
    )

    df = df.drop(columns=["n", "id"], errors="ignore")

    df["X_bite"] = pd.to_numeric(df["X_bite"], errors="coerce")
    df["Y_bite"] = pd.to_numeric(df["Y_bite"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

    df["X_bite"] = df["X_bite"].astype(str).str.replace(",", ".").astype(float)
    df["Y_bite"] = df["Y_bite"].astype(str).str.replace(",", ".").astype(float)

    df = df.dropna(subset=["X_bite", "Y_bite", "date"])

    df["date"] = df["date"].dt.date

    values = [
        {
            "date_of_bite": row.date,
            "x": float(row.X_bite),
            "y": float(row.Y_bite),
            "location": row.get("location"),
        }
        for _, row in df.iterrows()
    ]

    stmt = text("""
        INSERT INTO bites (
            date_of_bite,
            point_of_bite,
            location_description,
            cluster_id
        )
        SELECT
            :date_of_bite,
            ST_SetSRID(ST_MakePoint(:x, :y), 4326),
            :location,
            c.id
        FROM clusters c
        WHERE ST_Contains(
            c.geometry,
            ST_SetSRID(ST_MakePoint(:x, :y), 4326)
        )
    """).bindparams(
        bindparam("date_of_bite", type_=Date),
        bindparam("x", type_=Float),
        bindparam("y", type_=Float),
        bindparam("location", type_=String),
    )

    async with async_session_maker() as session:
        await session.execute(stmt, values)
        await session.commit()

    print(f"Импортировано {len(values)} записей")
    print("Перенос завершён")


if __name__ == "__main__":
    asyncio.run(main())


