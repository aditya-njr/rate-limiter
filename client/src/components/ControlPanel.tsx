import type { Algorithm } from '../api';

type Props = {
  algorithm: Algorithm;
  onAlgorithm: (a: Algorithm) => void;
  clientId: string;
  onClientId: (v: string) => void;
  requestCount: number;
  onRequestCount: (v: number) => void;
  intervalMs: number;
  onIntervalMs: (v: number) => void;
  fixedSliding: { windowMs: number; maxRequests: number };
  onFixedSliding: (v: { windowMs: number; maxRequests: number }) => void;
  token: { capacity: number; refillPerSecond: number };
  onToken: (v: { capacity: number; refillPerSecond: number }) => void;
  leaky: { capacity: number; leakPerSecond: number };
  onLeaky: (v: { capacity: number; leakPerSecond: number }) => void;
  onRun: () => void;
  onReset: () => void;
  loading: boolean;
};

const algoLabels: Record<Algorithm, string> = {
  fixedWindow: 'Fixed window',
  slidingWindow: 'Sliding window (log)',
  tokenBucket: 'Token bucket',
  leakyBucket: 'Leaky bucket',
};

export function ControlPanel(props: Props) {
  const {
    algorithm,
    onAlgorithm,
    clientId,
    onClientId,
    requestCount,
    onRequestCount,
    intervalMs,
    onIntervalMs,
    fixedSliding,
    onFixedSliding,
    token,
    onToken,
    leaky,
    onLeaky,
    onRun,
    onReset,
    loading,
  } = props;

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-6 shadow-xl backdrop-blur">
      <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-400">
        Simulation
      </h2>
      <div className="grid gap-4 md:grid-cols-2">
        <label className="block text-sm">
          <span className="mb-1 block text-slate-400">Algorithm</span>
          <select
            className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100 outline-none ring-sky-500/40 focus:ring-2"
            value={algorithm}
            onChange={(e) => onAlgorithm(e.target.value as Algorithm)}
          >
            {(Object.keys(algoLabels) as Algorithm[]).map((k) => (
              <option key={k} value={k}>
                {algoLabels[k]}
              </option>
            ))}
          </select>
        </label>
        <label className="block text-sm">
          <span className="mb-1 block text-slate-400">Client ID (session key for /try)</span>
          <input
            className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-sm text-slate-100 outline-none ring-sky-500/40 focus:ring-2"
            value={clientId}
            onChange={(e) => onClientId(e.target.value)}
          />
        </label>
        <label className="block text-sm">
          <span className="mb-1 block text-slate-400">Request count</span>
          <input
            type="number"
            min={1}
            max={10000}
            className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100 outline-none ring-sky-500/40 focus:ring-2"
            value={requestCount}
            onChange={(e) => onRequestCount(Number(e.target.value))}
          />
        </label>
        <label className="block text-sm">
          <span className="mb-1 block text-slate-400">Interval (ms between virtual requests)</span>
          <input
            type="number"
            min={0}
            max={60000}
            className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100 outline-none ring-sky-500/40 focus:ring-2"
            value={intervalMs}
            onChange={(e) => onIntervalMs(Number(e.target.value))}
          />
        </label>
      </div>

      <div className="mt-4 rounded-lg border border-slate-800 bg-slate-900/50 p-4">
        <p className="mb-3 text-xs font-medium uppercase tracking-wide text-slate-500">Parameters</p>
        {(algorithm === 'fixedWindow' || algorithm === 'slidingWindow') && (
          <div className="grid gap-3 md:grid-cols-2">
            <label className="text-sm">
              <span className="mb-1 block text-slate-400">Window (ms)</span>
              <input
                type="number"
                min={1}
                className="w-full rounded border border-slate-700 bg-slate-950 px-2 py-1.5 font-mono text-sm"
                value={fixedSliding.windowMs}
                onChange={(e) =>
                  onFixedSliding({ ...fixedSliding, windowMs: Number(e.target.value) })
                }
              />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-400">Max requests / window</span>
              <input
                type="number"
                min={1}
                className="w-full rounded border border-slate-700 bg-slate-950 px-2 py-1.5 font-mono text-sm"
                value={fixedSliding.maxRequests}
                onChange={(e) =>
                  onFixedSliding({ ...fixedSliding, maxRequests: Number(e.target.value) })
                }
              />
            </label>
          </div>
        )}
        {algorithm === 'tokenBucket' && (
          <div className="grid gap-3 md:grid-cols-2">
            <label className="text-sm">
              <span className="mb-1 block text-slate-400">Burst capacity (tokens)</span>
              <input
                type="number"
                min={1}
                className="w-full rounded border border-slate-700 bg-slate-950 px-2 py-1.5 font-mono text-sm"
                value={token.capacity}
                onChange={(e) => onToken({ ...token, capacity: Number(e.target.value) })}
              />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-400">Refill (tokens / second)</span>
              <input
                type="number"
                min={0.0001}
                step={0.1}
                className="w-full rounded border border-slate-700 bg-slate-950 px-2 py-1.5 font-mono text-sm"
                value={token.refillPerSecond}
                onChange={(e) => onToken({ ...token, refillPerSecond: Number(e.target.value) })}
              />
            </label>
          </div>
        )}
        {algorithm === 'leakyBucket' && (
          <div className="grid gap-3 md:grid-cols-2">
            <label className="text-sm">
              <span className="mb-1 block text-slate-400">Queue capacity</span>
              <input
                type="number"
                min={1}
                className="w-full rounded border border-slate-700 bg-slate-950 px-2 py-1.5 font-mono text-sm"
                value={leaky.capacity}
                onChange={(e) => onLeaky({ ...leaky, capacity: Number(e.target.value) })}
              />
            </label>
            <label className="text-sm">
              <span className="mb-1 block text-slate-400">Leak rate (units / second)</span>
              <input
                type="number"
                min={0.0001}
                step={0.1}
                className="w-full rounded border border-slate-700 bg-slate-950 px-2 py-1.5 font-mono text-sm"
                value={leaky.leakPerSecond}
                onChange={(e) => onLeaky({ ...leaky, leakPerSecond: Number(e.target.value) })}
              />
            </label>
          </div>
        )}
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <button
          type="button"
          disabled={loading}
          onClick={onRun}
          className="rounded-lg bg-sky-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-sky-900/30 transition hover:bg-sky-500 disabled:opacity-50"
        >
          {loading ? 'Running…' : 'Run simulation'}
        </button>
        <button
          type="button"
          onClick={onReset}
          className="rounded-lg border border-slate-600 bg-slate-900 px-5 py-2.5 text-sm font-medium text-slate-200 hover:bg-slate-800"
        >
          Reset server session
        </button>
      </div>
    </div>
  );
}
