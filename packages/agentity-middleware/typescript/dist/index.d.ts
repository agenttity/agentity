import type { Request, Response, NextFunction } from 'express';
export interface AgentityMiddlewareOptions {
    registryUrl?: string;
    toleranceSeconds?: number;
}
export declare function agentityMiddleware(opts?: AgentityMiddlewareOptions): (req: Request, res: Response, next: NextFunction) => Promise<void>;
