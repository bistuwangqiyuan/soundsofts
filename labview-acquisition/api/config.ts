import type { VercelRequest, VercelResponse } from "./types";
import fs from "fs";
// @ts-ignore - no types
import ini from "ini";
import { corsHeaders } from "./_lib/cors";
import { defaultParamsPath } from "./_lib/config-path";

export default async function handler(req: VercelRequest, res: VercelResponse) {
  for (const [k, v] of Object.entries(corsHeaders)) res.setHeader(k, v);
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "GET") return res.status(405).json({ error: "Method not allowed" });

  try {
    const raw = fs.readFileSync(defaultParamsPath, "utf-8");
    const parsed = ini.parse(raw) as Record<string, Record<string, string>>;
    return res.status(200).json(parsed);
  } catch (e: any) {
    return res.status(500).json({ error: e?.message ?? "Internal error" });
  }
}
