import { useState } from "react";
import {
  HiOutlineClock,
  HiOutlineTrash,
  HiOutlineChevronDown,
  HiOutlineChevronUp,
  HiOutlineCheckCircle,
  HiOutlineXCircle,
} from "react-icons/hi";
import type { HistoryEntry, Provider } from "../types";
import { getTagStyle } from "../utils/tagStyles";

const PROVIDER_LABELS: Record<Provider, string> = {
  claude: "Claude AI",
  classic: "Clássico",
  huggingface: "HuggingFace",
};

const PROVIDER_STYLES: Record<Provider, string> = {
  claude: "bg-violet-500/10 text-violet-400 border-violet-500/20",
  classic: "bg-sky-500/10 text-sky-400 border-sky-500/20",
  huggingface: "bg-amber-500/10 text-amber-400 border-amber-500/20",
};

interface Props {
  history: HistoryEntry[];
  onClear: () => void;
  onSelect: (entry: HistoryEntry) => void;
}

export function History({ history, onClear, onSelect }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [providerFilter, setProviderFilter] = useState<Provider | "all">("all");

  const providers = Array.from(new Set(history.map((e) => e.provider))) as Provider[];
  const filtered = providerFilter === "all" ? history : history.filter((e) => e.provider === providerFilter);

  //if (history.length === 0) return null;


  return (
    history.length === 0 ? (
      <div className="bg-white dark:bg-card rounded-xl border border-gray-200 dark:border-border p-5 space-y-3 transition-colors">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-medium text-zinc-400 uppercase tracking-widest flex items-center gap-2">
            <HiOutlineClock className="text-sm" />
            Histórico
            <span className="text-zinc-600">({history.length})</span>
          </h3>
        </div>
        <p className="text-sm text-gray-700 dark:text-zinc-300">
          Nenhuma classificação realizada ainda.
        </p>
      </div>
    ) : ( 
    <div className="bg-white dark:bg-card rounded-xl border border-gray-200 dark:border-border p-5 space-y-3 transition-colors">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-medium text-zinc-400 uppercase tracking-widest flex items-center gap-2">
          <HiOutlineClock className="text-sm" />
          Histórico
          <span className="text-zinc-600">({filtered.length})</span>
        </h3>
        <button
          onClick={onClear}
          className="flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-md border border-red-500/20 hover:bg-red-500/8 text-red-400/70 hover:text-red-400 transition-all duration-200"
        >
          <HiOutlineTrash className="text-sm" />
          Limpar
        </button>
      </div>

      {providers.length > 0 && (
        <div className="flex items-center gap-1.5 flex-wrap">
          <button
            onClick={() => setProviderFilter("all")}
            className={`px-2.5 py-1 rounded-md text-xs font-medium border transition-all duration-200 ${
              providerFilter === "all"
                ? "bg-zinc-700/60 text-zinc-200 border-zinc-600"
                : "text-zinc-500 border-transparent hover:border-zinc-700 hover:text-zinc-300"
            }`}
          >
            Todos
          </button>
          {providers.map((p) => (
            <button
              key={p}
              onClick={() => setProviderFilter(p)}
              className={`px-2.5 py-1 rounded-md text-xs font-medium border transition-all duration-200 ${
                providerFilter === p
                  ? PROVIDER_STYLES[p]
                  : "text-zinc-500 border-transparent hover:border-zinc-700 hover:text-zinc-300"
              }`}
            >
              {PROVIDER_LABELS[p]}
            </button>
          ))}
        </div>
      )}

      <div className="space-y-0.5">
        {(expanded ? filtered : filtered.slice(0, 3)).map((entry) => (
          <button
            key={entry.id}
            onClick={() => onSelect(entry)}
            className="w-full text-left px-3 py-2.5 rounded-lg border border-transparent hover:border-gray-200 dark:hover:border-border hover:bg-gray-50 dark:hover:bg-card-hover transition-all duration-200 group"
          >
            <div className="flex items-center gap-3">
              <div
                className={`shrink-0 ${
                  entry.category === "Produtivo"
                    ? "text-emerald-500"
                    : "text-zinc-500"
                }`}
              >
                {entry.category === "Produtivo" ? (
                  <HiOutlineCheckCircle className="text-base" />
                ) : (
                  <HiOutlineXCircle className="text-base" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-700 dark:text-zinc-300 truncate">
                  {entry.summary}
                </p>
                <div className="flex items-center gap-2 mt-0.5 flex-wrap">
                  <span
                    className={`text-xs ${
                      entry.category === "Produtivo"
                        ? "text-emerald-500"
                        : "text-zinc-500"
                    }`}
                  >
                    {entry.category}
                  </span>
                  {(() => {
                    const s = getTagStyle(entry.tag);
                    return (
                      <span className={`text-xs px-1.5 py-0.5 rounded border font-medium ${s.bg} ${s.text} ${s.border}`}>
                        {entry.tag}
                      </span>
                    );
                  })()}
                  <span className="text-xs text-zinc-700">&middot;</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded border font-medium ${PROVIDER_STYLES[entry.provider]}`}>
                    {PROVIDER_LABELS[entry.provider]}
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

      {filtered.length > 3 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-center gap-1 py-1.5 text-xs text-zinc-500 hover:text-zinc-300 transition-all duration-200"
        >
          {expanded ? (
            <>
              <HiOutlineChevronUp className="text-sm" />
              Mostrar menos
            </>
          ) : (
            <>
              <HiOutlineChevronDown className="text-sm" />
              Ver todos ({filtered.length})
            </>
          )}
        </button>
      )}
    </div>
  ));
}
