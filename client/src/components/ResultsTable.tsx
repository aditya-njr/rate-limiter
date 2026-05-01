import type { SimulateResultRow } from '../api';

export function ResultsTable({ rows }: { rows: SimulateResultRow[] | null }) {
  if (!rows?.length) return null;
  const tail = rows.slice(-40);

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-800">
      <table className="w-full min-w-[480px] text-left text-sm">
        <thead className="bg-slate-900/80 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-3 py-2 font-medium">#</th>
            <th className="px-3 py-2 font-medium">nowMs</th>
            <th className="px-3 py-2 font-medium">Result</th>
            <th className="px-3 py-2 font-medium">Remaining</th>
            <th className="px-3 py-2 font-medium">Retry (ms)</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800 font-mono text-xs text-slate-300">
          {tail.map((r) => (
            <tr key={r.index} className="hover:bg-slate-900/50">
              <td className="px-3 py-1.5">{r.index}</td>
              <td className="px-3 py-1.5">{r.nowMs}</td>
              <td className="px-3 py-1.5">
                <span
                  className={
                    r.allowed ? 'rounded bg-emerald-500/15 px-1.5 text-emerald-400' : 'rounded bg-red-500/15 px-1.5 text-red-400'
                  }
                >
                  {r.allowed ? 'allow' : 'deny'}
                </span>
              </td>
              <td className="px-3 py-1.5">{r.remaining ?? '—'}</td>
              <td className="px-3 py-1.5">
                {r.retryAfterMs !== undefined ? r.retryAfterMs.toFixed(1) : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length > 40 && (
        <p className="border-t border-slate-800 bg-slate-900/40 px-3 py-2 text-xs text-slate-500">
          Showing last 40 of {rows.length} rows.
        </p>
      )}
    </div>
  );
}
