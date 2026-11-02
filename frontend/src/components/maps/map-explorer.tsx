
"use client";

import { useEffect, useRef } from "react";

import maplibregl from "maplibre-gl";
import type { Map } from "maplibre-gl";
import { useMapStore } from "@/store/map.store";

export default function MapExplorer() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<Map | null>(null);

  const setSelectedLocation = useMapStore(
    (state) => state.setSelectedLocation,
  );

  useEffect(() => {
    if (!mapContainer.current || mapInstance.current) {
      return;
    }

    const map = new maplibregl.Map({
      container: mapContainer.current,
      style:
        process.env.NEXT_PUBLIC_MAP_STYLE_URL ??
        "https://tiles.openfreemap.org/styles/liberty",
      center: [79.8612, 6.9271],
      zoom: 11,
      attributionControl: true,
    });

    map.addControl(
      new maplibregl.NavigationControl(),
      "top-right",
    );

    map.on("click", (event) => {
      setSelectedLocation(
        event.lngLat.lat,
        event.lngLat.lng,
      );
    });

    mapInstance.current = map;

    return () => {
      map.remove();
      mapInstance.current = null;
    };
  }, [setSelectedLocation]);

  return (
    <div className="relative h-full min-h-[420px] w-full overflow-hidden rounded-xl">
      <div
        ref={mapContainer}
        className="absolute inset-0"
      />
    </div>
  );
}
