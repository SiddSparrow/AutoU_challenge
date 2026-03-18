import { HiOutlineCheckCircle, HiOutlineXCircle } from "react-icons/hi";
import type { ClassificationResponse } from "../types";

interface Props {
  result: ClassificationResponse;
}

export function ResultCard({ result }: Props) {
  const isProdutivo = result.category === "Produtivo";
  const confidencePercent = Math.round(result.confidence * 100);

  return (
    <div className="bg-white rounded-2xl shadow-md border border-gray-100 p-6 space-y-5 animate-fade-in">
      <h3 className="text-lg font-semibold text-gray-800">
        Resultado da Classificação
      </h3>

      {/* Category Badge */}
      <div className="flex items-center gap-3">
        <div
          className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold ${
            isProdutivo
              ? "bg-emerald-100 text-emerald-700"
              : "bg-gray-100 text-gray-600"
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
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>Confiança</span>
            <span className="font-medium">{confidencePercent}%</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                isProdutivo ? "bg-emerald-500" : "bg-gray-400"
              }`}
              style={{ width: `${confidencePercent}%` }}
            />
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="bg-gray-50 rounded-xl p-4">
        <p className="text-xs font-medium text-gray-500 mb-1 uppercase tracking-wide">
          Resumo
        </p>
        <p className="text-gray-700 text-sm">{result.summary}</p>
      </div>
    </div>
  );
}
