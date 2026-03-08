/** Request/Response types for Vercel serverless handlers */
export interface VercelRequest {
  method?: string;
  body?: any;
}

export interface VercelResponse {
  setHeader(name: string, value: string): void;
  status(code: number): VercelResponse;
  json(body: any): void;
  end(): void;
}
