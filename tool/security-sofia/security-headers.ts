import type { Request, Response, NextFunction } from 'express';

// Applies to the API, admin assets, temporary review and error responses.
export function securityHeaders(_req: Request, res: Response, next: NextFunction): void {
  res.setHeader('Strict-Transport-Security', 'max-age=31536000');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  next();
}
