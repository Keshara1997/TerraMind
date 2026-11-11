
"use client";

import { useQuery, useMutation } from "@tanstack/react-query";
import { captureService } from "@/services/capture.service";

type Props = {
  projectId: string;
  captureId: string;
};

type Dataset = {
  id: string;
  name: string;
  format: string;
  processing_status: string;
  metadata: {
    output?: {
      features?: Array<{
        id: string;
        properties?: Record<string, unknown>;
        assets?: Record<string, { href?: string }>;
      }>;
    };
    statistics?: {
      min?: number;
      max?: number;
      mean?: number;
      median?: number;
    };
    processing_error?: string;
  };
  statistics?: {
    min?: number;
    max?: number;
    mean?: number;
    median?: number;
  };
};

export default function NDVISceneList({
  projectId,
  captureId,
}: Props) {
  const datasetsQuery = useQuery({
    queryKey: ["capture-datasets", projectId, captureId],
    queryFn: () =>
      captureService.getDatasets(projectId, captureId),
    refetchInterval: (query) => {
      const datasets = query.state.data ?? [];
      return datasets.some(
        (dataset) =>
          dataset.processing_status === "pending" ||
          dataset.processing_status === "running",
      )
        ? 3000
        : false;
    },
  });

  const mutation = useMutation({
    mutationFn: ({
      datasetId,
      itemId,
    }: {
      datasetId: string;
      itemId: string;
    }) =>
      captureService.processNDVI(
        projectId,
        captureId,
        datasetId,
        itemId,
      ),
    onSuccess: () => datasetsQuery.refetch(),
  });

  const downloadMutation = useMutation({
    mutationFn: async (datasetId: string) => {
      const blob = await captureService.download(
        projectId,
        captureId,
        datasetId,
      );

      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${datasetId}.tif`;
      anchor.click();
      URL.revokeObjectURL(url);
    },
  });

  const datasets = datasetsQuery.data ?? [];

  const stacDatasets = datasets.filter(
    (dataset) => dataset.format === "stac-json",
  );

  const ndviDatasets = datasets.filter(
    (dataset) => dataset.format === "geotiff",
  );

  return (
    <div className="mt-4 space-y-4">
      <section className="rounded-lg border p-4">
        <h3 className="font-semibold">Satellite scenes</h3>

        {stacDatasets.map((dataset) => {
          const features =
            dataset.metadata?.output?.features ?? [];

          return (
            <div key={dataset.id} className="mt-3 space-y-3">
              {features.length === 0 && (
                <p className="text-sm text-gray-500">
                  No satellite scenes matched this search.
                </p>
              )}

              {features.map((feature) => {
                const properties = feature.properties ?? {};
                const cloudCover = properties["eo:cloud_cover"];

                return (
                  <div
                    key={feature.id}
                    className="rounded-lg border p-3"
                  >
                    <p className="break-all text-sm font-medium">
                      {feature.id}
                    </p>

                    <p className="mt-1 text-xs text-gray-500">
                      Acquired:{" "}
                      {String(properties.datetime ?? "Unknown")}
                    </p>

                    <p className="text-xs text-gray-500">
                      Cloud cover:{" "}
                      {cloudCover == null
                        ? "Not provided"
                        : `${cloudCover}%`}
                    </p>

                    <button
                      type="button"
                      disabled={mutation.isPending}
                      onClick={() =>
                        mutation.mutate({
                          datasetId: dataset.id,
                          itemId: feature.id,
                        })
                      }
                      className="mt-3 rounded-lg bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50"
                    >
                      Process NDVI
                    </button>
                  </div>
                );
              })}
            </div>
          );
        })}
      </section>

      <section className="rounded-lg border p-4">
        <h3 className="font-semibold">Processed raster datasets</h3>

        {ndviDatasets.length === 0 && (
          <p className="mt-3 text-sm text-gray-500">
            No NDVI datasets generated yet.
          </p>
        )}

        {ndviDatasets.map((dataset) => (
          <div
            key={dataset.id}
            className="mt-3 rounded-lg border p-3"
          >
            <p className="break-all text-sm font-medium">
              {dataset.name}
            </p>

            <p className="mt-1 text-sm capitalize text-gray-500">
              {dataset.processing_status}
            </p>

            {dataset.metadata?.processing_error && (
              <p className="mt-2 text-sm text-red-600">
                {dataset.metadata.processing_error}
              </p>
            )}

            {dataset.processing_status === "completed" && (
              <>
                <p className="mt-2 text-sm">
                  Mean NDVI:{" "}
                  {dataset.statistics?.mean?.toFixed(4) ?? "N/A"}
                </p>

                <button
                  type="button"
                  onClick={() =>
                    downloadMutation.mutate(dataset.id)
                  }
                  className="mt-3 rounded-lg border px-4 py-2 text-sm"
                >
                  Download GeoTIFF
                </button>
              </>
            )}
          </div>
        ))}
      </section>

      {mutation.isError && (
        <p className="text-sm text-red-600">
          Unable to start NDVI processing.
        </p>
      )}

      {datasetsQuery.isError && (
        <p className="text-sm text-red-600">
          Unable to load dataset records.
        </p>
      )}
    </div>
  );
}
