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
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-md border border-gray-100 dark:border-gray-700 p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 flex items-center gap-2">
          <HiOutlineClock className="text-xl" />
          Histórico
          <span className="text-sm font-normal text-gray-400 dark:text-gray-500">
            ({history.length})
          </span>
        </h3>
        <button
          onClick={onClear}
          className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg transition-all bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/40 text-red-600 dark:text-red-400"
        >
          <HiOutlineTrash className="text-sm" />
          Limpar
        </button>
      </div>

      <div className="space-y-2">
        {displayed.map((entry) => (
          <button
            key={entry.id}
            onClick={() => onSelect(entry)}
            className="w-full text-left p-3 rounded-xl border border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-all group"
          >
            <div className="flex items-center gap-3">
              <div
                className={`flex-shrink-0 p-1 rounded-full ${
                  entry.category === "Produtivo"
                    ? "text-emerald-500"
                    : "text-gray-400"
                }`}
              >
                {entry.category === "Produtivo" ? (
                  <HiOutlineCheckCircle className="text-lg" />
                ) : (
                  <HiOutlineXCircle className="text-lg" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-700 dark:text-gray-200 truncate">
                  {entry.summary}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  <span
                    className={`text-xs font-medium ${
                      entry.category === "Produtivo"
                        ? "text-emerald-600 dark:text-emerald-400"
                        : "text-gray-500 dark:text-gray-400"
                    }`}
                  >
                    {entry.category}
                  </span>
                  <span className="text-xs text-gray-400 dark:text-gray-500">
                    {Math.round(entry.confidence * 100)}%
                  </span>
                  <span className="text-xs text-gray-400 dark:text-gray-500">
                    &middot;
                  </span>
                  <span className="text-xs text-gray-400 dark:text-gray-500">
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
          className="w-full flex items-center justify-center gap-1 py-2 text-xs font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-all"
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
