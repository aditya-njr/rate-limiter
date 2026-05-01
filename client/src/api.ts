export type Algorithm = 'fixedWindow' | 'slidingWindow' | 'tokenBucket' | 'leakyBucket';

export type SimulateConfig =
  | { windowMs: number; maxRequests: number }
  | { capacity: number; refillPerSecond: number }
  | { capacity: number; leakPerSecond: number };

export type SimulateRequest = {
  algorithm: Algorithm;
  clientId: string;
  requestCount: number;
  intervalMs?: number;
  config: SimulateConfig;
};

export type SimulateResultRow = {
  index: number;
  nowMs: number;
  allowed: boolean;
  retryAfterMs?: number;
  remaining?: number;
};

export type SimulateResponse = {
  algorithm: Algorithm;
  clientId: string;
  summary: { total: number; allowed: number; rejected: number };
  results: SimulateResultRow[];
};

/** Empty in dev → same-origin + Vite proxy. Set VITE_API_URL for production or direct API host. */
export function getApiBase(): string {
  const raw = import.meta.env.VITE_API_URL;
  return (typeof raw === 'string' ? raw : '').replace(/\/$/, '');
}

export async function simulate(body: SimulateRequest): Promise<SimulateResponse> {
  const base = getApiBase();
  const res = await fetch(`${base}/api/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = (await res.json().catch(() => ({}))) as { error?: { message?: string } };
    throw new Error(err.error?.message ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<SimulateResponse>;
}

export async function resetSession(clientId: string, algorithm?: Algorithm): Promise<{ removed: number }> {
  const base = getApiBase();
  const res = await fetch(`${base}/api/reset`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ clientId, algorithm }),
  });
  if (!res.ok) {
    const err = (await res.json().catch(() => ({}))) as { error?: { message?: string } };
    throw new Error(err.error?.message ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<{ removed: number }>;
}

export async function health(): Promise<{ status: string }> {
  const base = getApiBase();
  const url = `${base}/health`;
  try {
    const res = await fetch(url);
    if (!res.ok) {
      console.warn('[api] health HTTP', res.status, url);
      throw new Error(`Health check failed: HTTP ${res.status}`);
    }
    const data = (await res.json()) as { status: string };
    console.log('[api] health OK', url, data);
    return data;
  } catch (e) {
    console.error('[api] health error', url, e);
    throw e;
  }
}
