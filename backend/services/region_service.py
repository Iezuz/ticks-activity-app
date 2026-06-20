from typing import Sequence, Optional


from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from models import Region
from repositories.region_repo import create_region, list_regions, get_region

#GRID_CELL_SIZE_METERS = 5000


class RegionService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self) -> Sequence[Region]:
        return await list_regions(self.db)

    async def get_by_id(self, region_id: int) -> Optional[Region]:
        return await get_region(self.db, region_id)

    async def create_region_with_grid(
        self,
        *,
        name: str,
        boundary_wkt: str,
        description: str | None = None,
    ) -> Region:

        try:
            region = await create_region(
                self.db,
                name=name,
                boundary_wkt=boundary_wkt,
                description=description
            )

            #created_count = await generate_clusters_for_region(self.db, region_id=region.id)

            #print(f"Created {created_count} clusters")

            await self.db.commit()
            await self.db.refresh(region)

            return region

        except SQLAlchemyError:
            await self.db.rollback()
            raise



