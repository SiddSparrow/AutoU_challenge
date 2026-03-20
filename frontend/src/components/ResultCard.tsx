import { HiOutlineCheckCircle, HiOutlineXCircle, HiOutlineTag } from "react-icons/hi";
import type { ClassificationResponse } from "../types";
import { getTagStyle } from "../utils/tagStyles";

interface Props {
  result: ClassificationResponse;
}

export function ResultCard({ result }: Props) {
  const isProdutivo = result.category === "Produtivo";
  const tagStyle = getTagStyle(result.tag);

  return (
    <div className="bg-white dark:bg-card rounded-xl border border-gray-200 dark:border-border p-5 space-y-4 animate-fade-in transition-colors">
      <p className="text-xs font-medium text-zinc-400 uppercase tracking-widest">
        Resultado
      </p>

      {/* Category + Tag */}
      <div className="flex items-center flex-wrap gap-2">
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

        <div
          className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold border ${tagStyle.bg} ${tagStyle.text} ${tagStyle.border}`}
        >
          <HiOutlineTag className="text-sm" />
          {result.tag}
        </div>
      </div>

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
