
"use client";

import { useEffect, useRef, useState } from "react";
import { Map as MapLibre, NavigationControl } from "maplibre-gl";
import type { Map } from "maplibre-gl";
import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import {
  rasterService,
  type RasterInfo,
} from "@/services/raster.service";

type Props = {
  projectId: string;
  captureId: string;
  datasetId: string;
};

const SOURCE_ID = "aleph-ndvi-source";
const LAYER_ID = "aleph-ndvi-layer";

const MAP_STYLE =
  "https://tiles.openfreemap.org/styles/liberty";

function getAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  // Use the exact token key from your authentication service.
  return sessionStorage.getItem("access_token");
}

export default function RasterLayerViewer({
  projectId,
  captureId,
  datasetId,
}: Props) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<Map | null>(null);

  const [opacity, setOpacity] = useState(0.8);
  const [visible, setVisible] = useState(true);

  // Fetch raster information.
  const infoQuery = useQuery({
    queryKey: [
      "raster-info",
      projectId,
      captureId,
      datasetId,
    ],
    queryFn: () =>
      rasterService.getInfo(
        projectId,
        captureId,
        datasetId
      ),
    enabled: Boolean(projectId && captureId && datasetId),
  });

  // Initialize MapLibre with secure authentication.
  useEffect(() => {
    if (!mapContainer.current || mapRef.current) {
      return;
    }

    const apiBaseURL = api.defaults.baseURL?.replace(/\/$/, "");

    const apiOrigin = apiBaseURL
      ? new URL(apiBaseURL, window.location.origin).origin
      : "";

    const map = new MapLibre({
      container: mapContainer.current,

      style: MAP_STYLE,

      center: [79.8612, 6.9271],

      zoom: 10,

      transformRequest: (url) => {
        const token = getAccessToken();

        let requestOrigin: string;

        try {
          requestOrigin = new URL(
            url,
            window.location.origin
          ).origin;
        } catch {
          return { url };
        }

        // Never send the TerraMind access token
        // to external map providers.
        if (
          !apiOrigin ||
          requestOrigin !== apiOrigin
        ) {
          return { url };
        }

        // Attach authentication only to backend requests.
        return {
          url,
          headers: token
            ? {
                Authorization: `Bearer ${token}`,
              }
            : {},
        };
      },
    });

    map.addControl(
      new NavigationControl(),
      "top-right"
    );

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Load raster layer.
  useEffect(() => {
    const map = mapRef.current;
    const info = infoQuery.data;

    if (!map || !info) {
      return;
    }

    const addRaster = () => {
      // Remove previous raster layer.
      if (map.getLayer(LAYER_ID)) {
        map.removeLayer(LAYER_ID);
      }

      // Remove previous raster source.
      if (map.getSource(SOURCE_ID)) {
        map.removeSource(SOURCE_ID);
      }

      const baseUrl = api.defaults.baseURL?.replace(
        /\/$/,
        ""
      );

      if (!baseUrl) {
        console.error(
          "API base URL is not configured."
        );
        return;
      }

      const tilePath = rasterService.tilePath(
        projectId,
        captureId,
        datasetId
      );

      const tileURL = `${baseUrl}${tilePath}`;

      // Add authenticated backend raster source.
      map.addSource(SOURCE_ID, {
        type: "raster",
        tiles: [tileURL],
        tileSize: 256,
      });

      // Add raster visualization layer.
      map.addLayer({
        id: LAYER_ID,
        type: "raster",
        source: SOURCE_ID,

        paint: {
          "raster-opacity": opacity,
        },

        layout: {
          visibility: visible
            ? "visible"
            : "none",
        },
      });

      // Zoom to raster boundaries.
      if (info.bounds) {
        map.fitBounds(
          [
            [
              info.bounds.left,
              info.bounds.bottom,
            ],
            [
              info.bounds.right,
              info.bounds.top,
            ],
          ],
          {
            padding: 40,
            maxZoom: 15,
          }
        );
      }
    };

    if (map.isStyleLoaded()) {
      addRaster();
    } else {
      map.once("load", addRaster);
    }

    return () => {
      map.off("load", addRaster);
    };
  }, [
    infoQuery.data,
    projectId,
    captureId,
    datasetId,
  ]);

  // Update raster opacity.
  useEffect(() => {
    const map = mapRef.current;

    if (map?.getLayer(LAYER_ID)) {
      map.setPaintProperty(
        LAYER_ID,
        "raster-opacity",
        opacity
      );
    }
  }, [opacity]);

  // Update raster visibility.
  useEffect(() => {
    const map = mapRef.current;

    if (map?.getLayer(LAYER_ID)) {
      map.setLayoutProperty(
        LAYER_ID,
        "visibility",
        visible ? "visible" : "none"
      );
    }
  }, [visible]);

  // Loading state.
  if (infoQuery.isLoading) {
    return (
      <p className="p-4">
        Loading raster information...
      </p>
    );
  }

  // Error state.
  if (infoQuery.isError || !infoQuery.data) {
    return (
      <p className="p-4 text-sm text-red-600">
        Unable to load raster information.
      </p>
    );
  }

  const info: RasterInfo = infoQuery.data;

  return (
    <div className="space-y-4">

      {/* Raster information */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border p-4">

        <div>
          <h2 className="font-semibold">
            {info.name}
          </h2>

          <p className="text-xs text-gray-500">
            {info.crs ?? "Unknown CRS"} · NDVI GeoTIFF
          </p>
        </div>

        {/* Layer visibility */}
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={visible}
            onChange={(event) =>
              setVisible(event.target.checked)
            }
          />

          Show layer
        </label>

      </div>

      {/* MapLibre map */}
      <div
        ref={mapContainer}
        className="h-[550px] w-full overflow-hidden rounded-xl border"
      />

      {/* Opacity control */}
      <div className="rounded-lg border p-4">

        <div className="flex justify-between">

          <label className="font-medium">
            Layer opacity
          </label>

          <span className="text-sm text-gray-500">
            {Math.round(opacity * 100)}%
          </span>

        </div>

        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={opacity}
          onChange={(event) =>
            setOpacity(
              Number(event.target.value)
            )
          }
          className="mt-3 w-full"
        />

      </div>

      {/* NDVI legend */}
      <div className="rounded-lg border p-4">

        <h3 className="font-semibold">
          NDVI legend
        </h3>

        <div className="mt-3 h-4 rounded-full bg-gradient-to-r from-red-600 via-yellow-300 to-green-700" />

        <div className="mt-2 flex justify-between text-xs text-gray-500">

          <span>-1.0 · Low</span>

          <span>0 · Neutral</span>

          <span>+1.0 · High</span>

        </div>

      </div>

      {/* Raster statistics */}
      {info.statistics && (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">

          {[
            ["Minimum", info.statistics.min],
            ["Maximum", info.statistics.max],
            ["Mean", info.statistics.mean],
            ["Median", info.statistics.median],
          ].map(([label, value]) => (

            <div
              key={String(label)}
              className="rounded-lg border p-3"
            >

              <p className="text-xs text-gray-500">
                {label}
              </p>

              <p className="mt-1 text-lg font-semibold">

                {typeof value === "number"
                  ? value.toFixed(3)
                  : "N/A"}

              </p>

            </div>

          ))}

        </div>
      )}

    </div>
  );
}
