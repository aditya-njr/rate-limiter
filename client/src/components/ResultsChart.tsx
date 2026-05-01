import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { SimulateResultRow } from '../api';

type Point = {
  index: number;
  allowedCum: number;
  rejectedCum: number;
};

function buildSeries(rows: SimulateResultRow[]): Point[] {
  let a = 0;
  let r = 0;
  return rows.map((row) => {
    if (row.allowed) a += 1;
    else r += 1;
    return { index: row.index, allowedCum: a, rejectedCum: r };
  });
}

export function ResultsChart({ rows }: { rows: SimulateResultRow[] | null }) {
  if (!rows?.length) {
    return (
      <div className="flex h-72 items-center justify-center rounded-xl border border-dashed border-slate-700 text-sm text-slate-500">
        Run a simulation to see cumulative allow / deny curves.
      </div>
    );
  }

  const data = buildSeries(rows);

  return (
    <div className="h-80 w-full rounded-xl border border-slate-800 bg-slate-950/40 p-4">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="gOk" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#34d399" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#34d399" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="gDeny" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f87171" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#f87171" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis dataKey="index" tick={{ fill: '#94a3b8', fontSize: 11 }} stroke="#334155" />
          <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} stroke="#334155" allowDecimals={false} />
          <Tooltip
            contentStyle={{
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: 8,
            }}
            labelStyle={{ color: '#e2e8f0' }}
          />
          <Legend />
          <Area
            type="monotone"
            dataKey="allowedCum"
            name="Allowed (cumulative)"
            stroke="#34d399"
            fill="url(#gOk)"
            strokeWidth={2}
          />
          <Area
            type="monotone"
            dataKey="rejectedCum"
            name="Rejected (cumulative)"
            stroke="#f87171"
            fill="url(#gDeny)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
