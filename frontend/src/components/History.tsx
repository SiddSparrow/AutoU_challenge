import { useState } from "react";
import {
  HiOutlineClock,
  HiOutlineTrash,
  HiOutlineChevronDown,
  HiOutlineChevronUp,
  HiOutlineCheckCircle,
  HiOutlineXCircle,
} from "react-icons/hi";
import type { HistoryEntry } from "../types";

interface Props {
  history: HistoryEntry[];
  onClear: () => void;
  onSelect: (entry: HistoryEntry) => void;
}

export function History({ history, onClear, onSelect }: Props) {
  const [expanded, setExpanded] = useState(false);

  if (history.length === 0) return null;

  const displayed = expanded ? history : history.slice(0, 3);

  return (
    <div className="bg-white dark:bg-card rounded-2xl border border-gray-200 dark:border-border p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-zinc-500 uppercase tracking-wider flex items-center gap-2">
          <HiOutlineClock className="text-base" />
          Histórico
          <span className="text-zinc-600">({history.length})</span>
        </h3>
        <button
          onClick={onClear}
          className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg transition-all border border-red-500/20 hover:bg-red-500/10 text-red-400"
        >
          <HiOutlineTrash className="text-sm" />
          Limpar
        </button>
      </div>

      <div className="space-y-1">
        {displayed.map((entry) => (
          <button
            key={entry.id}
            onClick={() => onSelect(entry)}
            className="w-full text-left p-3 rounded-xl border border-transparent hover:border-border hover:bg-gray-50 dark:hover:bg-card-hover transition-all group"
          >
            <div className="flex items-center gap-3">
              <div
                className={`flex-shrink-0 ${
                  entry.category === "Produtivo"
                    ? "text-emerald-500"
                    : "text-zinc-500"
                }`}
              >
                {entry.category === "Produtivo" ? (
                  <HiOutlineCheckCircle className="text-lg" />
                ) : (
                  <HiOutlineXCircle className="text-lg" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-700 dark:text-zinc-300 truncate">
                  {entry.summary}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  <span
                    className={`text-xs font-medium ${
                      entry.category === "Produtivo"
                        ? "text-emerald-500"
                        : "text-zinc-500"
                    }`}
                  >
                    {entry.category}
                  </span>
                  <span className="text-xs text-zinc-600">
                    {Math.round(entry.confidence * 100)}%
                  </span>
                  <span className="text-xs text-zinc-700">&middot;</span>
                  <span className="text-xs text-zinc-600">
                    {new Date(entry.timestamp).toLocaleDateString("pt-BR", {
                      day: "2-digit",
                      month: "2-digit",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>

      {history.length > 3 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-center gap-1 py-2 text-xs font-medium text-zinc-500 hover:text-zinc-300 transition-all"
        >
          {expanded ? (
            <>
              <HiOutlineChevronUp />
              Mostrar menos
            </>
          ) : (
            <>
              <HiOutlineChevronDown />
              Ver todos ({history.length})
            </>
          )}
        </button>
      )}
    </div>
  );
}
