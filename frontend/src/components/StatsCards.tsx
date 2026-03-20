import { useState } from "react";
import {
  BarChart,
  Bar,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  HiOutlineCheckCircle,
  HiOutlineXCircle,
  HiOutlineChevronDown,
  HiOutlineChevronUp,
  HiOutlineTag,
  HiOutlineX,
} from "react-icons/hi";
import type { HistoryEntry, EmailTag } from "../types";
import { useTheme } from "../contexts/ThemeContext";
import { getTagStyle } from "../utils/tagStyles";

type Period = "day" | "week" | "month";

interface Props {
  history: HistoryEntry[];
  onSelectEntry: (entry: HistoryEntry) => void;
}

const PERIOD_LABELS: Record<Period, string> = { day: "Dia", week: "Semana", month: "Mês" };

function periodKey(ts: string, period: Period): string {
  const d = new Date(ts);
  if (period === "day") {
    return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" });
  }
  if (period === "week") {
    const offset = d.getDay() === 0 ? 6 : d.getDay() - 1;
    const monday = new Date(d);
    monday.setDate(d.getDate() - offset);
    return monday.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit" });
  }
  return d.toLocaleDateString("pt-BR", { month: "short", year: "2-digit" });
}

function buildVolumeData(history: HistoryEntry[], period: Period) {
  const counts: Record<string, number> = {};
  for (const e of history) {
    const k = periodKey(e.timestamp, period);
    counts[k] = (counts[k] ?? 0) + 1;
  }
  const seen = new Set<string>();
  const ordered: { label: string; total: number }[] = [];
  for (const e of [...history].reverse()) {
    const k = periodKey(e.timestamp, period);
    if (!seen.has(k)) {
      seen.add(k);
      ordered.push({ label: k, total: counts[k] });
    }
  }
  return ordered;
}

function filterByPeriod(history: HistoryEntry[], period: Period, key: string) {
  return history.filter((e) => periodKey(e.timestamp, period) === key);
}

function getTagsInPeriod(history: HistoryEntry[], period: Period, key: string) {
  const entries = filterByPeriod(history, period, key);
  const map: Partial<Record<EmailTag, HistoryEntry[]>> = {};
  for (const e of entries) {
    if (!map[e.tag]) map[e.tag] = [];
    map[e.tag]!.push(e);
  }
  return map;
}

export function StatsCards({ history, onSelectEntry }: Props) {
  const { theme } = useTheme();
  const chartColor = theme === "dark" ? "#8b5cf6" : "#4361ee";
  const [period, setPeriod] = useState<Period>("day");
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [openTag, setOpenTag] = useState<EmailTag | null>(null);

  if (history.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-zinc-600 text-sm">
        Nenhuma classificação realizada ainda.
      </div>
    );
  }

  const volumeData = buildVolumeData(history, period);

  // Default selected key to the latest period bucket
  const activeKey = selectedKey ?? volumeData[volumeData.length - 1]?.label ?? null;
  const tagMap = activeKey ? getTagsInPeriod(history, period, activeKey) : {};
  const tagEntries = Object.entries(tagMap) as [EmailTag, HistoryEntry[]][];

  const handlePeriodChange = (p: Period) => {
    setPeriod(p);
    setSelectedKey(null);
    setOpenTag(null);
  };

  return (
    <div className="space-y-6">
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
                onClick={() => handlePeriodChange(p)}
                className={`px-2.5 py-1 text-xs rounded-md border transition-colors ${
                  period === p
                    ? "border-violet-500/40 bg-violet-500/10 text-violet-400"
                    : "border-gray-200 dark:border-border text-zinc-500 hover:text-zinc-300"
                }`}
              >
                {PERIOD_LABELS[p]}
              </button>
            ))}
          </div>
        </div>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={volumeData}
              margin={{ left: 0, right: 8 }}
              style={{ cursor: "pointer" }}
            >
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
                cursor={{ fill: "rgba(139,92,246,0.08)" }}
              />
              <Bar
                dataKey="total"
                radius={[4, 4, 0, 0]}
                maxBarSize={48}
                fill={chartColor}
                onClick={(data) => {
                  const label = (data as unknown as { label: string }).label;
                  setSelectedKey(label);
                  setOpenTag(null);
                }}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
        {activeKey && (
          <p className="text-xs text-zinc-500 mt-3 text-center">
            Período selecionado: <span className="text-zinc-300">{activeKey}</span>
            {" — clique em uma barra para filtrar"}
          </p>
        )}
      </div>

      {/* Tag breakdown cards */}
      {activeKey && tagEntries.length > 0 && (
        <div className="bg-white dark:bg-card rounded-xl border border-gray-200 dark:border-border p-6 transition-colors">
          <p className="text-xs font-medium text-zinc-400 uppercase tracking-widest mb-4">
            Tags em <span className="text-zinc-300">{activeKey}</span>
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {tagEntries
              .sort((a, b) => b[1].length - a[1].length)
              .map(([tag, entries]) => {
                const s = getTagStyle(tag);
                const isOpen = openTag === tag;
                return (
                  <button
                    key={tag}
                    onClick={() => setOpenTag(isOpen ? null : tag)}
                    className={`text-left p-3 rounded-lg border transition-all duration-200 ${s.bg} ${s.border} hover:opacity-90`}
                  >
                    <div className="flex items-center justify-between gap-1">
                      <div className="flex items-center gap-1.5">
                        <HiOutlineTag className={`text-xs shrink-0 ${s.text}`} />
                        <span className={`text-xs font-semibold ${s.text} leading-tight`}>
                          {tag}
                        </span>
                      </div>
                      {isOpen
                        ? <HiOutlineChevronUp className={`text-xs shrink-0 ${s.text}`} />
                        : <HiOutlineChevronDown className={`text-xs shrink-0 ${s.text}`} />
                      }
                    </div>
                    <p className={`text-lg font-bold mt-1 ${s.text}`}>{entries.length}</p>
                    <p className="text-[10px] text-zinc-500 mt-0.5">
                      {entries.length === 1 ? "email" : "emails"}
                    </p>
                  </button>
                );
              })}
          </div>

          {/* Inline email list for selected tag */}
          {openTag && tagMap[openTag] && (
            <div className="mt-4 border border-gray-100 dark:border-border rounded-lg overflow-hidden">
              <div className="flex items-center justify-between px-3 py-2 bg-gray-50 dark:bg-base border-b border-gray-100 dark:border-border">
                <span className="text-xs font-medium text-zinc-400 uppercase tracking-widest">
                  {openTag} — {tagMap[openTag]!.length} email{tagMap[openTag]!.length !== 1 ? "s" : ""}
                </span>
                <button
                  onClick={() => setOpenTag(null)}
                  className="text-zinc-500 hover:text-zinc-300 transition-colors"
                >
                  <HiOutlineX className="text-sm" />
                </button>
              </div>
              <div className="divide-y divide-gray-100 dark:divide-border">
                {tagMap[openTag]!.map((entry) => (
                  <button
                    key={entry.id}
                    onClick={() => onSelectEntry(entry)}
                    className="w-full text-left px-3 py-2.5 hover:bg-gray-50 dark:hover:bg-card-hover transition-colors"
                  >
                    <div className="flex items-start gap-2.5">
                      <div className={`shrink-0 mt-0.5 ${entry.category === "Produtivo" ? "text-emerald-500" : "text-zinc-500"}`}>
                        {entry.category === "Produtivo"
                          ? <HiOutlineCheckCircle className="text-base" />
                          : <HiOutlineXCircle className="text-base" />
                        }
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-700 dark:text-zinc-300 truncate">
                          {entry.summary}
                        </p>
                        <p className="text-xs text-zinc-600 mt-0.5">
                          {new Date(entry.timestamp).toLocaleString("pt-BR", {
                            day: "2-digit",
                            month: "2-digit",
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
