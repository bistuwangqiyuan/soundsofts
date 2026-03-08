/** CORS headers for frontend access */
export const corsHeaders: Record<string, string> = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
  "Access-Control-Max-Age": "86400",
};

export function withCors(res: any, status: number, body: object | string) {
  for (const [k, v] of Object.entries(corsHeaders)) res.setHeader(k, v);
  res.status(status).json(typeof body === "string" ? { error: body } : body);
}
