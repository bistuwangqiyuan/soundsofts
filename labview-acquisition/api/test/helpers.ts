import type { VercelRequest, VercelResponse } from "../types";

export function createMockRes(): VercelResponse & { _status?: number; _json?: any; _headers: Record<string, string> } {
  const out = {
    _status: undefined as number | undefined,
    _json: undefined as any,
    _headers: {} as Record<string, string>,
    setHeader(k: string, v: string) {
      this._headers[k] = v;
    },
    status(code: number) {
      this._status = code;
      return this;
    },
    json(body: any) {
      this._json = body;
      return this;
    },
    end() {
      return this;
    },
  };
  return out;
}

export function createMockReq(overrides: Partial<VercelRequest> = {}): VercelRequest {
  return { method: "GET", ...overrides };
}
