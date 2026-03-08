import { describe, it, expect } from "vitest";
import handler from "../calibration";
import { createMockReq, createMockRes } from "./helpers";

describe("GET /api/calibration", () => {
  it("returns 200 and full calibration JSON on GET", async () => {
    const req = createMockReq({ method: "GET" });
    const res = createMockRes();
    await handler(req, res as any);
    expect(res._status).toBe(200);
    expect(res._json).toBeDefined();
    expect(res._json.force_sensor).toBeDefined();
    expect(res._json.force_sensor.calibration_points).toBeInstanceOf(Array);
    expect(res._json.position_encoder).toBeDefined();
    expect(res._json.position_encoder.mm_per_pulse).toBe(0.02);
  });

  it("returns 204 on OPTIONS", async () => {
    const req = createMockReq({ method: "OPTIONS" });
    const res = createMockRes();
    await handler(req, res as any);
    expect(res._status).toBe(204);
  });

  it("returns 405 for POST", async () => {
    const req = createMockReq({ method: "POST" });
    const res = createMockRes();
    await handler(req, res as any);
    expect(res._status).toBe(405);
    expect(res._json?.error).toContain("Method not allowed");
  });

  it("sets CORS headers", async () => {
    const req = createMockReq({ method: "GET" });
    const res = createMockRes();
    await handler(req, res as any);
    expect(res._headers["Access-Control-Allow-Origin"]).toBe("*");
  });
});
