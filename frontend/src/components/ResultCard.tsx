import { HiOutlineCheckCircle, HiOutlineXCircle } from "react-icons/hi";
import type { ClassificationResponse } from "../types";

interface Props {
  result: ClassificationResponse;
}

export function ResultCard({ result }: Props) {
  const isProdutivo = result.category === "Produtivo";
  const confidencePercent = Math.round(result.confidence * 100);

  return (
    <div className="bg-white dark:bg-card rounded-2xl border border-gray-200 dark:border-border p-6 space-y-5 animate-fade-in">
      <h3 className="text-sm font-medium text-zinc-500 uppercase tracking-wider">
        Resultado da Classificação
      </h3>

      {/* Category Badge */}
      <div className="flex items-center gap-3">
        <div
          className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold ${
            isProdutivo
              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
              : "bg-zinc-500/10 text-zinc-400 border border-zinc-500/20"
          }`}
        >
          {isProdutivo ? (
            <HiOutlineCheckCircle className="text-lg" />
          ) : (
            <HiOutlineXCircle className="text-lg" />
          )}
          {result.category}
        </div>

        {/* Confidence */}
        <div className="flex-1">
          <div className="flex justify-between text-xs text-zinc-500 mb-1.5">
            <span>Confiança</span>
            <span className="font-semibold text-zinc-300">{confidencePercent}%</span>
          </div>
          <div className="h-2 bg-gray-100 dark:bg-base rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-700 bg-accent"
              style={{ width: `${confidencePercent}%` }}
            />
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="bg-gray-50 dark:bg-base rounded-xl p-4 border border-gray-100 dark:border-border">
        <p className="text-xs font-medium text-zinc-500 mb-1.5 uppercase tracking-wider">
          Resumo
        </p>
        <p className="text-gray-700 dark:text-zinc-200 text-sm leading-relaxed">{result.summary}</p>
      </div>
    </div>
  );
}
