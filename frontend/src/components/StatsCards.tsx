import {
  AreaChart,
  Area,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { HistoryEntry } from "../types";
import { useTheme } from "../contexts/ThemeContext";

interface Props {
  history: HistoryEntry[];
}

export function StatsCards({ history }: Props) {
  const { theme } = useTheme();
  const chartColor = theme === "dark" ? "#8b5cf6" : "#4361ee";

  if (history.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-zinc-600 text-sm">
        Nenhuma classificação realizada ainda.
      </div>
    );
  }

  if (history.length < 2) {
    return (
      <div className="flex items-center justify-center h-48 text-zinc-600 text-sm">
        Classifique ao menos 2 emails para ver o gráfico.
      </div>
    );
  }

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
    <div className="bg-white dark:bg-card rounded-xl border border-gray-200 dark:border-border p-6 transition-colors">
      <p className="text-xs font-medium text-zinc-400 uppercase tracking-widest mb-6">
        Confiança por Classificação
      </p>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ left: 0, right: 8 }}>
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
  );
}
