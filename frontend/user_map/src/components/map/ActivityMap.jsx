import { useEffect, useMemo, useRef } from "react";

import {
  MapContainer,
  TileLayer,
  GeoJSON,
  useMap,
} from "react-leaflet";

import L from "leaflet";

import "leaflet/dist/leaflet.css";
import "leaflet.markercluster";
import "leaflet.heat";

function FitBounds({ geojson }) {

  const map = useMap();

  useEffect(() => {

    if (!geojson) {
      return;
    }

    const layer = L.geoJSON(geojson);

    const bounds = layer.getBounds();

    if (bounds.isValid()) {
      map.fitBounds(bounds, {
        padding: [20, 20],
      });
    }

  }, [geojson, map]);

  return null;
}

function getClusterColor(value) {

  if (value === null || value === undefined) {
    return "#00000000";
  }

  if (value <= 0) {
    return "#00000000";
  }

  if (value < 3) {
    return "#ffcccc";
  }

  if (value < 7) {
    return "#ff9999";
  }

  if (value < 15) {
    return "#ff4d4d";
  }

  if (value < 30) {
    return "#e60000";
  }

  return "#990000";
}

export default function ActivityMap({
  region,
  activityClusters,
  bites,
  bitesVisible,
  bitesMode,
}) {

  const mapRef = useRef(null);

  const markerLayerRef = useRef(null);

  const heatLayerRef = useRef(null);

  const activityGeoJson = useMemo(() => {

    return {
      type: "FeatureCollection",
      features: activityClusters.map((cluster) => ({
        type: "Feature",
        geometry: JSON.parse(cluster.geometry),
        properties: {
          amount: cluster.amount,
        },
      })),
    };

  }, [activityClusters]);

  useEffect(() => {

    const map = mapRef.current;

    if (!map) {
      return;
    }

    if (markerLayerRef.current) {
      map.removeLayer(markerLayerRef.current);
    }

    if (heatLayerRef.current) {
      map.removeLayer(heatLayerRef.current);
    }

    if (!bitesVisible) {
      return;
    }

    const points = bites
      .filter((bite) => bite.point_of_bite)
      .map((bite) => {

        const coords = bite.point_of_bite.coordinates;

        return {
          lat: coords[1],
          lng: coords[0],
        };
      });

    if (bitesMode === "clusters") {

      const clusterGroup = L.markerClusterGroup();

      points.forEach((p) => {
        clusterGroup.addLayer(
          L.marker([p.lat, p.lng])
        );
      });

      markerLayerRef.current = clusterGroup;

      map.addLayer(clusterGroup);
    }

    if (bitesMode === "heatmap") {

      const heatData = points.map((p) => [
        p.lat,
        p.lng,
        1,
      ]);

      const heatLayer = L.heatLayer(
        heatData,
        {
          radius: 35,
          blur: 25,
          maxZoom: 17,
        }
      );

      heatLayerRef.current = heatLayer;

      map.addLayer(heatLayer);
    }

  }, [
    bites,
    bitesVisible,
    bitesMode,
  ]);

  return (
    <MapContainer
      center={[55.75, 37.61]}
      zoom={5}
      style={{
        width: "100%",
        height: "100vh",
      }}
      whenCreated={(map) => {
        mapRef.current = map;
      }}
    >
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {region?.boundary && (
        <FitBounds geojson={region.boundary} />
      )}

      {!bitesVisible && (
        <GeoJSON
          data={activityGeoJson}
          style={(feature) => ({
            color: "#222",
            weight: 1,
            fillColor: getClusterColor(
              feature.properties.amount
            ),
            fillOpacity: 0.7,
          })}
          onEachFeature={(feature, layer) => {

            const amount =
              feature.properties.amount ?? 0;

            layer.bindPopup(
              `Количество укусов: ${amount}`
            );
          }}
        />
      )}
    </MapContainer>
  );
}