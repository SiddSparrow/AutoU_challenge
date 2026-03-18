import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import {
  HiOutlineInbox,
  HiOutlineCheckCircle,
  HiOutlineXCircle,
  HiOutlineTrendingUp,
} from "react-icons/hi";
import type { HistoryEntry } from "../types";

interface Props {
  history: HistoryEntry[];
}

const COLORS = {
  Produtivo: "#10b981",
  Improdutivo: "#6b7280",
};

export function StatsCards({ history }: Props) {
  if (history.length === 0) return null;

  const produtivos = history.filter((e) => e.category === "Produtivo").length;
  const improdutivos = history.length - produtivos;
  const avgConfidence =
    history.reduce((sum, e) => sum + e.confidence, 0) / history.length;

  const chartData = [
    { name: "Produtivo", value: produtivos },
    { name: "Improdutivo", value: improdutivos },
  ].filter((d) => d.value > 0);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-md border border-gray-100 dark:border-gray-700 p-6 space-y-5">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 flex items-center gap-2">
        <HiOutlineTrendingUp className="text-xl" />
        Estatísticas
      </h3>

      <div className="grid grid-cols-3 gap-3">
        <StatCard
          icon={<HiOutlineInbox className="text-blue-500 text-xl" />}
          label="Total"
          value={history.length.toString()}
        />
        <StatCard
          icon={<HiOutlineCheckCircle className="text-emerald-500 text-xl" />}
          label="Produtivos"
          value={`${produtivos} (${Math.round((produtivos / history.length) * 100)}%)`}
        />
        <StatCard
          icon={<HiOutlineXCircle className="text-gray-400 text-xl" />}
          label="Improdutivos"
          value={`${improdutivos} (${Math.round((improdutivos / history.length) * 100)}%)`}
        />
      </div>

      <div className="flex items-center gap-6">
        {/* Donut Chart */}
        <div className="w-32 h-32 flex-shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={30}
                outerRadius={55}
                paddingAngle={3}
                dataKey="value"
                strokeWidth={0}
              >
                {chartData.map((entry) => (
                  <Cell
                    key={entry.name}
                    fill={COLORS[entry.name as keyof typeof COLORS]}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  borderRadius: "8px",
                  border: "none",
                  boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
                  fontSize: "12px",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Legend + Avg Confidence */}
        <div className="space-y-3 flex-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-emerald-500" />
            <span className="text-sm text-gray-600 dark:text-gray-300">Produtivo</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-gray-400" />
            <span className="text-sm text-gray-600 dark:text-gray-300">Improdutivo</span>
          </div>
          <div className="pt-2 border-t border-gray-100 dark:border-gray-700">
            <p className="text-xs text-gray-500 dark:text-gray-400">Confiança média</p>
            <p className="text-lg font-semibold text-gray-800 dark:text-gray-100">
              {Math.round(avgConfidence * 100)}%
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="bg-gray-50 dark:bg-gray-900 rounded-xl p-3 text-center space-y-1">
      <div className="flex justify-center">{icon}</div>
      <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
      <p className="text-sm font-semibold text-gray-800 dark:text-gray-100">{value}</p>
    </div>
  );
}
