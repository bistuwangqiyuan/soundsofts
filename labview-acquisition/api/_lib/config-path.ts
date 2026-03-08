import path from "path";

/** Project root (repo root on Vercel); Config is relative to it */
export const configDir = path.join(process.cwd(), "Config");

export const calibrationPath = path.join(configDir, "calibration_data.json");
export const defaultParamsPath = path.join(configDir, "default_params.ini");
