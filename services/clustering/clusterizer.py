from dataclasses import dataclass


@dataclass
class ClusterResult:
    polygon_wkt: str
    bite_ids: list[int]


class Clusterizer:

    def build_clusters(self, bites) -> list[ClusterResult]:
        pass

