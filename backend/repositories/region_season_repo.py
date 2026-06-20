from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy.dialects.postgresql import insert

from backend.models import Cluster, RegionSeason, Region
from backend.models.cluster_data import ClusterData


async def get_years_for_regions(db: AsyncSession, region_ids: list[int]) -> list[int]:

    result = await db.execute(
        select(func.extract("year", ClusterData.date).distinct())
        .join(Cluster, Cluster.id == ClusterData.cluster_id)
        .where(Cluster.region_id.in_(region_ids))
    )

    return [int(r[0]) for r in result.all()]


async def get_all_region_ids(db: AsyncSession):
    result = await db.execute(text("SELECT id FROM regions"))
    return [r[0] for r in result.fetchall()]


async def get_season_by_bites(db: AsyncSession, region_id: int, year: int) -> date | None:
    """
        Рассчитать дату начала сезона для региона в указанном году.
        Используется скользящее окно: при сумме укусов за 3 дня подряд >= 3 (весна).
        """
    min_total_growth = 3
    query = text(
        f"""
            WITH daily AS (
                SELECT
                    cd.date::date AS date,
                    COALESCE(SUM(cd.amount_of_bites), 0) AS bites
                FROM cluster_data cd
                JOIN clusters c ON c.id = cd.cluster_id
                WHERE c.region_id = :region_id
                  AND EXTRACT(YEAR FROM cd.date) = :year
                  AND EXTRACT(MONTH FROM cd.date) BETWEEN 3 AND 5
                GROUP BY cd.date
            ),
            full_range AS (
                SELECT generate_series(
                    DATE '{year}-03-01',
                    DATE '{year}-05-31',
                    INTERVAL '1 day'
                )::date AS date
            ),
            merged AS (
                SELECT
                    f.date,
                    COALESCE(d.bites, 0) AS bites
                FROM full_range f
                LEFT JOIN daily d ON d.date = f.date
            ),
            rolling AS (
                SELECT
                    date,
                    SUM(bites) OVER (
                        ORDER BY date
                        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
                    ) AS rolling_sum
                FROM merged
            )
            SELECT date
            FROM rolling
            WHERE rolling_sum >= :threshold
            ORDER BY date
            LIMIT 1
        """
    )
    result = await db.execute(
        query, {"region_id": region_id, "year": year, "threshold": min_total_growth}
    )
    row = result.first()
    return row[0] if row else None


# async def get_season_by_temperature(db: AsyncSession, region_id: int, year: int) -> date | None:
#     query = text("""
#         WITH daily AS (
#             SELECT
#                 cd.date::date AS date,
#                 AVG(cd.temperature) AS temp
#             FROM cluster_data cd
#             JOIN clusters c ON c.id = cd.cluster_id
#             WHERE c.region_id = :region_id
#               AND EXTRACT(YEAR FROM cd.date) = :year
#               AND cd.temperature IS NOT NULL
#             GROUP BY cd.date
#         ),
#         rolling AS (
#             SELECT
#                 date,
#                 AVG(temp) OVER (
#                     ORDER BY date
#                     ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
#                 ) AS temp_7d
#             FROM daily
#         )
#         SELECT date
#         FROM rolling
#         WHERE temp_7d >= :threshold
#         ORDER BY date
#         LIMIT 1
#     """)
#
#     result = await db.execute(query,
#                               {"region_id": region_id, "year": year, "threshold": TEMP_THRESHOLD})
#
#     row = result.first()
#     return row[0] if row else None


async def upsert_region_season_start(db: AsyncSession, region_id: int, year: int, season_start: date):
    stmt = (insert(RegionSeason).values(region_id=region_id, year=year,
                                        season_start_date=season_start).on_conflict_do_update(
        index_elements=["region_id", "year"],
        set_={"season_start_date": season_start}
    ))

    await db.execute(stmt)


async def get_region_centroid(db: AsyncSession, region_id: int):
    result = await db.execute(
        select(
            func.ST_Y(func.ST_Centroid(Region.boundary)),
            func.ST_X(func.ST_Centroid(Region.boundary)),
        ).where(Region.id == region_id)
    )

    row = result.first()

    if not row:
        return None, None

    return row[0], row[1]
