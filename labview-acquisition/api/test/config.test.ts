import { describe, it, expect } from "vitest";
import handler from "../config";
import { createMockReq, createMockRes } from "./helpers";

describe("GET /api/config", () => {
  it("returns 200 and parsed INI config as JSON", async () => {
    const req = createMockReq({ method: "GET" });
    const res = createMockRes();
    await handler(req, res as any);
    expect(res._status).toBe(200);
    expect(res._json).toBeDefined();
    expect(res._json.DAQ).toBeDefined();
    expect(res._json.DAQ.device).toBe("USB-6363");
    expect(res._json.DAQ.sample_rate).toBe("250000");
    expect(res._json.FPGA).toBeDefined();
    expect(res._json.Force).toBeDefined();
    expect(res._json.Storage).toBeDefined();
    expect(res._json.Alarm).toBeDefined();
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
  });

  it("sets CORS headers", async () => {
    const req = createMockReq({ method: "GET" });
    const res = createMockRes();
    await handler(req, res as any);
    expect(res._headers["Access-Control-Allow-Origin"]).toBe("*");
  });
});
