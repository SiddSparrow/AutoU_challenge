import {
  HiOutlineInbox,
  HiOutlineCheckCircle,
  HiOutlineXCircle,
  HiOutlineShieldExclamation,
} from "react-icons/hi";
import type { ClassificationResponse, HistoryEntry } from "../types";
import { ExportButtons } from "./ExportButtons";

interface Props {
  history: HistoryEntry[];
  result?: ClassificationResponse | null;
}

export function MiniStatsBar({ history, result }: Props) {
  if (history.length === 0) return null;

  const produtivos = history.filter((e) => e.category === "Produtivo").length;
  const improdutivos = history.length - produtivos;
  const alertas = history.filter(
    (e) => e.tag === "SPAM" || e.tag === "POSSÍVEL GOLPE"
  ).length;

  const stats = [
    {
      icon: <HiOutlineInbox className="text-accent" />,
      label: "Total",
      value: history.length.toString(),
      sub: null as string | null,
      subColor: "",
    },
    {
      icon: <HiOutlineCheckCircle className="text-emerald-500" />,
      label: "Produtivos",
      value: produtivos.toString(),
      sub: `${Math.round((produtivos / history.length) * 100)}%`,
      subColor: "text-emerald-500",
    },
    {
      icon: <HiOutlineXCircle className="text-zinc-500" />,
      label: "Improdutivos",
      value: improdutivos.toString(),
      sub: `${Math.round((improdutivos / history.length) * 100)}%`,
      subColor: "text-red-400",
    },
    {
      icon: <HiOutlineShieldExclamation className="text-red-400" />,
      label: "Alertas",
      value: alertas.toString(),
      sub: alertas > 0 ? "spam/golpe" : null,
      subColor: "text-red-400",
    },
  ];

  return (
    <div className="shrink-0 flex items-center gap-2 px-5 py-2.5 border-b border-slate-200 dark:border-border bg-gray-50 dark:bg-card overflow-x-auto transition-colors">
      {stats.map((stat, i) => (
        <div
          key={i}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-border bg-slate-50 dark:bg-base shrink-0"
        >
          <span className="text-sm leading-none">{stat.icon}</span>
          <div>
            <div className="flex items-baseline gap-1">
              <span className="text-xs font-semibold text-slate-800 dark:text-zinc-100 tabular-nums">
                {stat.value}
              </span>
              {stat.sub && (
                <span className={`text-xs ${stat.subColor}`}>{stat.sub}</span>
              )}
            </div>
            <p className="text-[10px] text-zinc-500 leading-none whitespace-nowrap mt-0.5">
              {stat.label}
            </p>
          </div>
        </div>
      ))}

      {result && (
        <div className="ml-auto shrink-0">
          <ExportButtons result={result} history={history} />
        </div>
      )}
    </div>
  );
}
