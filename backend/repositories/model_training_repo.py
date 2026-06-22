from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def get_short_term_dataset(db: AsyncSession):
    result = await db.execute(text("""
        SELECT
            cd.date,
            cd.cluster_id,
            c.elevation,
            cd.temperature,
            cd.precipitation,
            cd.cloudiness,
            cd.avg_number_of_imago_per_flag_hour,
            cd.avg_snow_depth,
            rs.season_start_date,
            cd.amount_of_bites
        FROM cluster_data cd
        JOIN clusters c ON c.id = cd.cluster_id
        JOIN region_season rs
            ON rs.region_id = c.region_id
           AND rs.year = EXTRACT(YEAR FROM cd.date)
        WHERE
            c.elevation IS NOT NULL
            AND rs.season_start_date IS NOT NULL
            AND cd.temperature IS NOT NULL
            AND cd.precipitation IS NOT NULL
            AND cd.cloudiness IS NOT NULL
            AND cd.avg_snow_depth IS NOT NULL
            AND rs.season_start_date IS NOT NULL
            AND cd.amount_of_bites IS NOT NULL
    """))

    rows = result.fetchall()

    X = []

    for r in rows:
        X.append({
            "date": r.date,
            "cluster_id": r.cluster_id,
            "elevation": r.elevation,
            "temperature": r.temperature,
            "precipitation": r.precipitation,
            "cloudiness": r.cloudiness,
            "avg_snow_depth": r.avg_snow_depth,
            "season_start_date": r.season_start_date,
            "avg_number_of_imago_per_flag_hour": r.avg_number_of_imago_per_flag_hour,
            "amount_of_bites": r.amount_of_bites
        })

    return X


async def get_long_term_dataset(db: AsyncSession):
    result = await db.execute(text("""
        SELECT
            cd.date,
            cd.cluster_id,
            c.elevation,
            cd.avg_snow_depth,
            rs.season_start_date,
            cd.amount_of_bites,
            cd.avg_number_of_imago_per_flag_hour
        FROM cluster_data cd
        JOIN clusters c ON c.id = cd.cluster_id
        JOIN region_season rs
            ON rs.region_id = c.region_id
           AND rs.year = EXTRACT(YEAR FROM cd.date)
        WHERE
            c.elevation IS NOT NULL
            AND rs.season_start_date IS NOT NULL
            AND cd.avg_snow_depth  IS NOT NULL
            AND rs.season_start_date IS NOT NULL
            AND cd.amount_of_bites IS NOT NULL
    """))

    rows = result.fetchall()

    X = []

    for r in rows:
        X.append({
            "date": r.date,
            "cluster_id": r.cluster_id,
            "elevation": r.elevation,
            "avg_snow_depth": r.avg_snow_depth,
            "season_start_date": r.season_start_date,
            "avg_number_of_imago_per_flag_hour": r.avg_number_of_imago_per_flag_hour,
            "amount_of_bites": r.amount_of_bites,
        })

    return X