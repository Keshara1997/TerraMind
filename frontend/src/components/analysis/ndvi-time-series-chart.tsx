"use client";

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { NDVITimeSeriesPoint } from "@/services/analysis.service";

interface Props {
  points: NDVITimeSeriesPoint[];
}

export default function NDVITimeSeriesChart({ points }: Props) {
  const data = points.map((point) => ({
    date: point.acquisition_date,
    mean: point.mean,
    minimum: point.minimum,
    maximum: point.maximum,
    median: point.median,
  }));

  if (data.length === 0) {
    return (
      <div className="rounded-xl border p-8 text-center text-sm text-gray-500">
        No completed NDVI observations are available for this period.
      </div>
    );
  }

  return (
    <div className="h-[360px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 15, right: 25, left: 5, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis domain={[-1, 1]} />
          <Tooltip />
          <Legend />

          <Line
            type="monotone"
            dataKey="mean"
            name="Mean NDVI"
            connectNulls
          />

          <Line
            type="monotone"
            dataKey="median"
            name="Median NDVI"
            connectNulls
          />

          <Line
            type="monotone"
            dataKey="minimum"
            name="Minimum NDVI"
            connectNulls
          />

          <Line
            type="monotone"
            dataKey="maximum"
            name="Maximum NDVI"
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}