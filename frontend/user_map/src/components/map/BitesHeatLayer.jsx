import { useEffect } from "react";

import { useMap } from "react-leaflet";

import L from "leaflet";
import "leaflet.heat";

export default function BitesHeatLayer({
  bites,
}) {

  const map = useMap();

  useEffect(() => {

    const points = bites.map((bite) => {

      const coords =
        bite.point_of_bite.coordinates;

      return [
        coords[1],
        coords[0],
        1,
      ];
    });

    const layer = L.heatLayer(points, {
      radius: 35,
      blur: 25,
      maxZoom: 17,
    });

    layer.addTo(map);

    return () => {
      map.removeLayer(layer);
    };

  }, [bites, map]);

  return null;
}