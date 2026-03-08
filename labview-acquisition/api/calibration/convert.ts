import type { VercelRequest, VercelResponse } from "../types";
import fs from "fs";
import { corsHeaders } from "../_lib/cors";
import { calibrationPath } from "../_lib/config-path";

function interp(x: number, xs: number[], ys: number[]): number {
  if (xs.length === 0) return x;
  if (x <= xs[0]) return ys[0];
  if (x >= xs[xs.length - 1]) return ys[ys.length - 1];
  let i = 0;
  while (i < xs.length - 1 && xs[i + 1] < x) i++;
  const t = (x - xs[i]) / (xs[i + 1] - xs[i]);
  return ys[i] + t * (ys[i + 1] - ys[i]);
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  for (const [k, v] of Object.entries(corsHeaders)) res.setHeader(k, v);
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  try {
    const raw = fs.readFileSync(calibrationPath, "utf-8");
    const data = JSON.parse(raw) as {
      force_sensor?: {
        calibration_points?: Array<{ voltage_v: number; force_n: number }>;
        zero_offset_mv?: number;
      };
      position_encoder?: { mm_per_pulse?: number };
    };
    const body = (req.body ?? {}) as Record<string, unknown>;
    const voltage_v = body.voltage_v != null ? Number(body.voltage_v) : null;
    const pulses = body.pulses != null ? Number(body.pulses) : null;
    const apply_zero = body.apply_zero !== false;

    const points = data.force_sensor?.calibration_points ?? [];
    const voltages = points.map((p) => p.voltage_v);
    const forces = points.map((p) => p.force_n);
    const zero_offset_mv = data.force_sensor?.zero_offset_mv ?? 0;
    const mm_per_pulse = data.position_encoder?.mm_per_pulse ?? 0.02;

    let force_n: number | null = null;
    let position_mm: number | null = null;
    if (voltage_v != null && !Number.isNaN(voltage_v)) {
      let v = voltage_v;
      if (apply_zero) v -= zero_offset_mv / 1000;
      force_n = points.length ? interp(v, voltages, forces) : v;
    }
    if (pulses != null && !Number.isNaN(pulses)) position_mm = pulses * mm_per_pulse;

    return res.status(200).json({ force_n, position_mm });
  } catch (e: any) {
    return res.status(500).json({ error: e?.message ?? "Internal error" });
  }
}
