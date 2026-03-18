import {
  AreaChart,
  Area,
  ResponsiveContainer,
  Tooltip,
  XAxis,
} from "recharts";
import {
  HiOutlineInbox,
  HiOutlineCheckCircle,
  HiOutlineXCircle,
} from "react-icons/hi";
import type { HistoryEntry } from "../types";

interface Props {
  history: HistoryEntry[];
}

export function StatsCards({ history }: Props) {
  if (history.length === 0) return null;

  const produtivos = history.filter((e) => e.category === "Produtivo").length;
  const improdutivos = history.length - produtivos;
  const avgConfidence =
    history.reduce((sum, e) => sum + e.confidence, 0) / history.length;

  // Build time-series data for the area chart (most recent last)
  const chartData = [...history]
    .reverse()
    .map((entry, i) => ({
      idx: i + 1,
      confidence: Math.round(entry.confidence * 100),
      label: new Date(entry.timestamp).toLocaleTimeString("pt-BR", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    }));

  return (
    <div className="space-y-4">
      {/* Stat Cards Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          icon={<HiOutlineInbox className="text-accent" />}
          label="Total Processados"
          value={history.length.toString()}
        />
        <MetricCard
          icon={<HiOutlineCheckCircle className="text-emerald-500" />}
          label="Produtivos"
          value={produtivos.toString()}
          delta={`${Math.round((produtivos / history.length) * 100)}%`}
          deltaPositive
        />
        <MetricCard
          icon={<HiOutlineXCircle className="text-zinc-400" />}
          label="Improdutivos"
          value={improdutivos.toString()}
          delta={`${Math.round((improdutivos / history.length) * 100)}%`}
          deltaPositive={false}
        />
        <MetricCard
          icon={<span className="text-accent text-lg">%</span>}
          label="Confiança Média"
          value={`${Math.round(avgConfidence * 100)}%`}
        />
      </div>

      {/* Area Chart */}
      {chartData.length >= 2 && (
        <div className="bg-white dark:bg-card rounded-2xl border border-gray-200 dark:border-border p-6">
          <p className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-4">
            Confiança por Classificação
          </p>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="gradientPurple" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#7c3aed" stopOpacity={0.4} />
                    <stop offset="100%" stopColor="#7c3aed" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="label"
                  tick={{ fontSize: 10, fill: "#71717a" }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    background: "#12121a",
                    border: "1px solid #1e1e2e",
                    borderRadius: "12px",
                    fontSize: "12px",
                    color: "#f1f1f5",
                  }}
                  formatter={(value) => [`${value}%`, "Confiança"]}
                />
                <Area
                  type="monotone"
                  dataKey="confidence"
                  stroke="#7c3aed"
                  strokeWidth={2}
                  fill="url(#gradientPurple)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({
  icon,
  label,
  value,
  delta,
  deltaPositive,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  delta?: string;
  deltaPositive?: boolean;
}) {
  return (
    <div className="bg-white dark:bg-card rounded-2xl border border-gray-200 dark:border-border p-5 space-y-3">
      <div className="text-xl">{icon}</div>
      <div>
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-gray-900 dark:text-zinc-100">
            {value}
          </span>
          {delta && (
            <span
              className={`text-sm font-medium ${
                deltaPositive ? "text-emerald-500" : "text-red-400"
              }`}
            >
              {delta}
            </span>
          )}
        </div>
        <p className="text-xs text-zinc-500 mt-1">{label}</p>
      </div>
    </div>
  );
}
