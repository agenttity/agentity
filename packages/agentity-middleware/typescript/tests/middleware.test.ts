import { describe, it, expect, vi } from 'vitest';
import { agentityMiddleware } from '../src/index.js';

function mockRequest(path: string, method = 'GET', headers: Record<string, string> = {}) {
  return { path, method, headers } as any;
}

function mockResponse() {
  const res: any = { statusCode: 200, body: {} };
  res.status = (code: number) => { res.statusCode = code; return res; };
  res.json = (body: any) => { res.body = body; return res; };
  return res;
}

describe('agentityMiddleware', () => {
  it('should pass through health endpoint', async () => {
    const middleware = agentityMiddleware();
    const req = mockRequest('/health');
    const res = mockResponse();
    const next = vi.fn();
    await middleware(req, res, next);
    expect(next).toHaveBeenCalled();
  });

  it('should reject missing headers', async () => {
    const middleware = agentityMiddleware();
    const req = mockRequest('/api/data');
    const res = mockResponse();
    const next = vi.fn();
    await middleware(req, res, next);
    expect(res.statusCode).toBe(401);
    expect(next).not.toHaveBeenCalled();
  });

  it('should reject nonce replay', async () => {
    const middleware = agentityMiddleware();
    const headers = {
      'agentity-token': 'test.token',
      'agentity-nonce': 'same-nonce',
      'agentity-timestamp': new Date().toISOString(),
    };
    const req1 = mockRequest('/api/data', 'GET', headers);
    const res1 = mockResponse();
    const next1 = vi.fn();
    await middleware(req1, res1, next1);

    const req2 = mockRequest('/api/data', 'GET', headers);
    const res2 = mockResponse();
    const next2 = vi.fn();
    await middleware(req2, res2, next2);
    expect(res2.statusCode).toBe(403);
  });
});
