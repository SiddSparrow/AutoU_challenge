import { useState } from "react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { HistoryEntry } from "../types";
import { useTheme } from "../contexts/ThemeContext";

type Period = "day" | "week" | "month";

interface Props {
  history: HistoryEntry[];
}

function buildVolumeData(history: HistoryEntry[], period: Period) {
  const counts: Record<string, number> = {};

  for (const entry of history) {
    const d = new Date(entry.timestamp);
    let key: string;

    if (period === "day") {
      key = d.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" });
    } else if (period === "week") {
      // ISO week: Monday-based
      const day = d.getDay() === 0 ? 6 : d.getDay() - 1; // 0=Mon
      const monday = new Date(d);
      monday.setDate(d.getDate() - day);
      key = monday.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" });
    } else {
      key = d.toLocaleDateString("pt-BR", { month: "short", year: "2-digit" });
    }

    counts[key] = (counts[key] ?? 0) + 1;
  }

  // Sort chronologically by reconstructing order from history timestamps
  const seen = new Set<string>();
  const ordered: { label: string; total: number }[] = [];
  for (const entry of [...history].reverse()) {
    const d = new Date(entry.timestamp);
    let key: string;
    if (period === "day") {
      key = d.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" });
    } else if (period === "week") {
      const day = d.getDay() === 0 ? 6 : d.getDay() - 1;
      const monday = new Date(d);
      monday.setDate(d.getDate() - day);
      key = monday.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" });
    } else {
      key = d.toLocaleDateString("pt-BR", { month: "short", year: "2-digit" });
    }
    if (!seen.has(key)) {
      seen.add(key);
      ordered.push({ label: key, total: counts[key] });
    }
  }
  return ordered;
}

export function StatsCards({ history }: Props) {
  const { theme } = useTheme();
  const chartColor = theme === "dark" ? "#8b5cf6" : "#4361ee";
  const [period, setPeriod] = useState<Period>("day");

  if (history.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-zinc-600 text-sm">
        Nenhuma classificação realizada ainda.
      </div>
    );
  }

  const confidenceData = [...history]
    .reverse()
    .map((entry, i) => ({
      idx: i + 1,
      confidence: Math.round(entry.confidence * 100),
      label: new Date(entry.timestamp).toLocaleTimeString("pt-BR", {
        hour: "2-digit",
        minute: "2-digit",
      }),
    }));

  const volumeData = buildVolumeData(history, period);

  const periodLabels: Record<Period, string> = {
    day: "Dia",
    week: "Semana",
    month: "Mês",
  };

  return (
    <div className="space-y-6">
      {/* Confidence chart */}
      {history.length >= 2 && (
        <div className="bg-white dark:bg-card rounded-xl border border-gray-200 dark:border-border p-6 transition-colors">
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-widest mb-6">
            Confiança por Classificação
          </p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={confidenceData} margin={{ left: 0, right: 8 }}>
                <defs>
                  <linearGradient id="gradientAccent" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={chartColor} stopOpacity={0.25} />
                    <stop offset="100%" stopColor={chartColor} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="label"
                  tick={{ fontSize: 10, fill: "#52525b" }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fontSize: 10, fill: "#52525b" }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) => `${v}%`}
                  width={34}
                />
                <Tooltip
                  contentStyle={{
                    background: "#141414",
                    border: "1px solid #252525",
                    borderRadius: "8px",
                    fontSize: "12px",
                    color: "#e4e4e7",
                  }}
                  formatter={(value) => [`${value}%`, "Confiança"]}
                  cursor={{ stroke: "#333333", strokeWidth: 1 }}
                />
                <Area
                  type="monotone"
                  dataKey="confidence"
                  stroke={chartColor}
                  strokeWidth={1.5}
                  fill="url(#gradientAccent)"
                  dot={{ r: 2.5, fill: chartColor, strokeWidth: 0 }}
                  activeDot={{ r: 4, fill: chartColor, strokeWidth: 0 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Volume chart */}
      <div className="bg-white dark:bg-card rounded-xl border border-gray-200 dark:border-border p-6 transition-colors">
        <div className="flex items-center justify-between mb-6">
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-widest">
            Volume de Emails
          </p>
          <div className="flex gap-1">
            {(["day", "week", "month"] as Period[]).map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-2.5 py-1 text-xs rounded-md border transition-colors ${
                  period === p
                    ? "border-violet-500/40 bg-violet-500/10 text-violet-400"
                    : "border-gray-200 dark:border-border text-zinc-500 hover:text-zinc-300"
                }`}
              >
                {periodLabels[p]}
              </button>
            ))}
          </div>
        </div>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={volumeData} margin={{ left: 0, right: 8 }}>
              <XAxis
                dataKey="label"
                tick={{ fontSize: 10, fill: "#52525b" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                allowDecimals={false}
                tick={{ fontSize: 10, fill: "#52525b" }}
                axisLine={false}
                tickLine={false}
                width={24}
              />
              <Tooltip
                contentStyle={{
                  background: "#141414",
                  border: "1px solid #252525",
                  borderRadius: "8px",
                  fontSize: "12px",
                  color: "#e4e4e7",
                }}
                formatter={(value) => [value, "Emails"]}
                cursor={{ fill: "rgba(139,92,246,0.06)" }}
              />
              <Bar
                dataKey="total"
                fill={chartColor}
                radius={[4, 4, 0, 0]}
                maxBarSize={48}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
