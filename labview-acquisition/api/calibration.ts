import type { VercelRequest, VercelResponse } from "./types";
import fs from "fs";
import { corsHeaders } from "./_lib/cors";
import { calibrationPath } from "./_lib/config-path";

/** GET /api/calibration — 返回完整校准数据 JSON */
export default async function handler(req: VercelRequest, res: VercelResponse) {
  for (const [k, v] of Object.entries(corsHeaders)) res.setHeader(k, v);
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "GET") return res.status(405).json({ error: "Method not allowed" });

  try {
    const raw = fs.readFileSync(calibrationPath, "utf-8");
    const data = JSON.parse(raw);
    return res.status(200).json(data);
  } catch (e: any) {
    return res.status(500).json({ error: e?.message ?? "Internal error" });
  }
}
