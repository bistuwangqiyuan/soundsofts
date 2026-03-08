import { describe, it, expect } from "vitest";
import handler from "../calibration/convert";
import { createMockReq, createMockRes } from "./helpers";

describe("POST /api/calibration/convert", () => {
  it("converts voltage_v and pulses to force_n and position_mm", async () => {
    const req = createMockReq({
      method: "POST",
      body: { voltage_v: 1.0, pulses: 100 },
    });
    const res = createMockRes();
    await handler(req, res as any);
    expect(res._status).toBe(200);
    expect(res._json.force_n).toBeDefined();
    expect(res._json.position_mm).toBe(2); // 100 * 0.02
    // 1.0 V with zero_offset 0.5mV -> ~0.9995 V -> interp to ~100 N
    expect(Math.abs(res._json.force_n - 100) < 1).toBe(true);
  });

  it("returns 405 for GET", async () => {
    const req = createMockReq({ method: "GET" });
    const res = createMockRes();
    await handler(req, res as any);
    expect(res._status).toBe(405);
  });

  it("returns 204 on OPTIONS", async () => {
    const req = createMockReq({ method: "OPTIONS" });
    const res = createMockRes();
    await handler(req, res as any);
    expect(res._status).toBe(204);
  });

  it("handles body with only voltage_v", async () => {
    const req = createMockReq({ method: "POST", body: { voltage_v: 5.0 } });
    const res = createMockRes();
    await handler(req, res as any);
    expect(res._status).toBe(200);
    expect(res._json.force_n).toBeCloseTo(500, 1); // zero_offset 会略减
    expect(res._json.position_mm).toBeNull();
  });

  it("handles body with only pulses", async () => {
    const req = createMockReq({ method: "POST", body: { pulses: 50 } });
    const res = createMockRes();
    await handler(req, res as any);
    expect(res._status).toBe(200);
    expect(res._json.force_n).toBeNull();
    expect(res._json.position_mm).toBe(1); // 50 * 0.02
  });

  it("handles empty body", async () => {
    const req = createMockReq({ method: "POST", body: {} });
    const res = createMockRes();
    await handler(req, res as any);
    expect(res._status).toBe(200);
    expect(res._json.force_n).toBeNull();
    expect(res._json.position_mm).toBeNull();
  });
});
