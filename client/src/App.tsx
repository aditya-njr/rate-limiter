import { useCallback, useEffect, useMemo, useState } from "react";
import type { Algorithm, SimulateRequest, SimulateResponse } from "./api";
import { health, resetSession, simulate } from "./api";
import { ControlPanel } from "./components/ControlPanel";
import { ResultsChart } from "./components/ResultsChart";
import { ResultsTable } from "./components/ResultsTable";

function defaultClientId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return `demo-${crypto.randomUUID().slice(0, 8)}`;
  }
  return `demo-${Math.random().toString(36).slice(2, 10)}`;
}

export function App() {
  const [algorithm, setAlgorithm] = useState<Algorithm>("tokenBucket");
  const [clientId, setClientId] = useState(defaultClientId);
  const [requestCount, setRequestCount] = useState(80);
  const [intervalMs, setIntervalMs] = useState(50);
  const [fixedSliding, setFixedSliding] = useState({
    windowMs: 1000,
    maxRequests: 5,
  });
  const [token, setToken] = useState({ capacity: 10, refillPerSecond: 2 });
  const [leaky, setLeaky] = useState({ capacity: 8, leakPerSecond: 3 });

  const [result, setResult] = useState<SimulateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiOk, setApiOk] = useState<boolean | null>(null);
  const [healthDetail, setHealthDetail] = useState<string | null>(null);

  useEffect(() => {
    health()
      .then(() => {
        setApiOk(true);
        setHealthDetail(null);
      })
      .catch((e) => {
        setApiOk(false);
        setHealthDetail(e instanceof Error ? e.message : String(e));
      });
  }, []);

  const buildRequest = useCallback((): SimulateRequest => {
    const base = {
      algorithm,
      clientId,
      requestCount,
      intervalMs,
    };
    if (algorithm === "fixedWindow" || algorithm === "slidingWindow") {
      return { ...base, config: { ...fixedSliding } };
    }
    if (algorithm === "tokenBucket") {
      return { ...base, config: { ...token } };
    }
    return { ...base, config: { ...leaky } };
  }, [
    algorithm,
    clientId,
    requestCount,
    intervalMs,
    fixedSliding,
    token,
    leaky,
  ]);

  const onRun = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await simulate(buildRequest());
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const onReset = async () => {
    try {
      await resetSession(clientId);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Reset failed");
    }
  };

  const summary = useMemo(() => result?.summary, [result]);

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <header className="mb-10">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="mb-1 text-xs font-semibold uppercase tracking-[0.2em] text-sky-400/90">
              ADITYA SINGH
            </p>
            <h1 className="text-3xl font-bold tracking-tight text-white md:text-4xl">
              Rate limiting algorithms
            </h1>
            <p className="mt-3 max-w-2xl text-slate-400">
              Compare fixed window, sliding window log, token bucket, and leaky
              bucket. Simulations use deterministic virtual time on the server
            </p>
          </div>
          <div className="flex max-w-md flex-col items-end gap-2 text-right">
            <div
              className={`rounded-full border px-3 py-1 text-xs font-medium ${
                apiOk === null
                  ? "border-slate-700 text-slate-500"
                  : apiOk
                    ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-400"
                    : "border-red-500/40 bg-red-500/10 text-red-400"
              }`}
            >
              {apiOk === null
                ? "Checking API…"
                : apiOk
                  ? "API reachable"
                  : "API unreachable from browser"}
            </div>
            {apiOk === false && healthDetail && (
              <p className="text-xs text-slate-500" title={healthDetail}>
                {healthDetail}. Check DevTools console for{" "}
                <code className="text-slate-400">[api]</code> logs. Ensure the
                API is on port 3001 or set{" "}
                <code className="text-slate-400">VITE_API_PROXY_TARGET</code> /{" "}
                <code className="text-slate-400">VITE_API_URL</code>.
              </p>
            )}
          </div>
        </div>
      </header>

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)]">
        <ControlPanel
          algorithm={algorithm}
          onAlgorithm={setAlgorithm}
          clientId={clientId}
          onClientId={setClientId}
          requestCount={requestCount}
          onRequestCount={setRequestCount}
          intervalMs={intervalMs}
          onIntervalMs={setIntervalMs}
          fixedSliding={fixedSliding}
          onFixedSliding={setFixedSliding}
          token={token}
          onToken={setToken}
          leaky={leaky}
          onLeaky={setLeaky}
          onRun={onRun}
          onReset={onReset}
          loading={loading}
        />

        {error && (
          <div className="rounded-lg border border-red-500/40 bg-red-950/40 px-4 py-3 text-sm text-red-200">
            {error}
          </div>
        )}

        {summary && (
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 px-4 py-3">
              <p className="text-xs uppercase tracking-wide text-slate-500">
                Total
              </p>
              <p className="text-2xl font-semibold text-white">
                {summary.total}
              </p>
            </div>
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 px-4 py-3">
              <p className="text-xs uppercase tracking-wide text-emerald-500/80">
                Allowed
              </p>
              <p className="text-2xl font-semibold text-emerald-400">
                {summary.allowed}
              </p>
            </div>
            <div className="rounded-xl border border-red-500/20 bg-red-500/5 px-4 py-3">
              <p className="text-xs uppercase tracking-wide text-red-400/80">
                Rejected
              </p>
              <p className="text-2xl font-semibold text-red-400">
                {summary.rejected}
              </p>
            </div>
          </div>
        )}

        <section>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-400">
            Cumulative outcomes
          </h2>
          <ResultsChart rows={result?.results ?? null} />
        </section>

        <section>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-400">
            Sample of requests
          </h2>
          <ResultsTable rows={result?.results ?? null} />
        </section>
      </div>

      <footer className="mt-16 border-t border-slate-800 pt-8 text-center text-xs text-slate-600">
        Server: FastAPI + Pydantic · Limiters are in-memory
      </footer>
    </div>
  );
}
