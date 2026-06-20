import { GeoJSON } from "react-leaflet";

import { getClusterColor } from "../../utils/colors";

export default function RegionPolygonsLayer({
  clusters,
}) {

  return (
    <>
      {clusters.map((cluster) => {

        const geometry = JSON.parse(cluster.geometry);

        return (
          <GeoJSON
            key={cluster.cluster_id}
            data={geometry}
            style={{
              color: "#333",
              weight: 1,
              fillColor: getClusterColor(cluster.amount),
              fillOpacity: 0.6,
            }}
          />
        );
      })}
    </>
  );
}