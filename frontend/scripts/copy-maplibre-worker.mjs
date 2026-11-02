import { copyFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const frontendDirectory = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const workerSource = resolve(
  frontendDirectory,
  "node_modules/maplibre-gl/dist/maplibre-gl-worker.mjs",
);
const workerDestination = resolve(
  frontendDirectory,
  "public/maplibre-gl-worker.mjs",
);

copyFileSync(workerSource, workerDestination);
