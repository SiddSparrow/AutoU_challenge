import { HiOutlineCheckCircle, HiOutlineXCircle, HiOutlineExclamationCircle } from "react-icons/hi";
import type { ClassificationResponse } from "../types";

interface Props {
  result: ClassificationResponse;
}

export function ResultCard({ result }: Props) {
  const isProdutivo = result.category === "Produtivo";
  const confidencePercent = Math.round(result.confidence * 100);

  return (
    <div className="bg-white dark:bg-card rounded-xl border border-gray-200 dark:border-border p-5 space-y-4 animate-fade-in transition-colors">
      <p className="text-xs font-medium text-zinc-400 uppercase tracking-widest">
        Resultado
      </p>

      {/* Category Badge */}
      <div
        className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium border ${
          isProdutivo
            ? "bg-emerald-500/8 text-emerald-400 border-emerald-500/20"
            : "bg-zinc-500/8 text-zinc-400 border-zinc-500/20"
        }`}
      >
        {isProdutivo ? (
          <HiOutlineCheckCircle className="text-sm" />
        ) : (
          <HiOutlineXCircle className="text-sm" />
        )}
        {result.category}
      </div>

      {/* Confidence */}
      <div className="space-y-1.5">
        <div className="flex justify-between items-center text-xs">
          <span className="text-zinc-500">Confiança</span>
          <span className="font-medium text-zinc-300 tabular-nums">
            {confidencePercent}%
          </span>
        </div>
        <div className="h-1 bg-gray-100 dark:bg-base rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{
              width: `${confidencePercent}%`,
              background: "linear-gradient(90deg, #7c3aed, #a78bfa)",
            }}
          />
        </div>
      </div>

      {/* Confidence flags */}
      {result.confidence_flags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {result.confidence_flags.map((flag) => (
            <span
              key={flag}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs bg-amber-500/8 text-amber-400 border border-amber-500/20"
            >
              <HiOutlineExclamationCircle className="shrink-0" />
              {flag}
            </span>
          ))}
        </div>
      )}

      {/* Summary */}
      <div className="pt-1 border-t border-gray-100 dark:border-border">
        <p className="text-xs text-zinc-500 mb-1.5 uppercase tracking-widest">
          Resumo
        </p>
        <p className="text-sm text-gray-700 dark:text-zinc-300 leading-relaxed">
          {result.summary}
        </p>
      </div>
    </div>
  );
}
