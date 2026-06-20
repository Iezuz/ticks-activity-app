import { useEffect } from "react";

import { useMap } from "react-leaflet";

import L from "leaflet";

import "leaflet.markercluster";

export default function BitesClusterLayer({
  bites,
}) {

  const map = useMap();

  useEffect(() => {

    const layer = L.markerClusterGroup();

    bites.forEach((bite) => {

      const coords =
        bite.point_of_bite.coordinates;

      const marker = L.marker([
        coords[1],
        coords[0],
      ]);

      layer.addLayer(marker);
    });

    map.addLayer(layer);

    return () => {
      map.removeLayer(layer);
    };

  }, [bites, map]);

  return null;
}