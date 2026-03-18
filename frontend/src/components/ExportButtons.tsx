import { HiOutlineDocumentDownload, HiOutlineTable } from "react-icons/hi";
import { exportResultPdf } from "../utils/exportPdf";
import { exportHistoryCsv } from "../utils/exportCsv";
import type { ClassificationResponse, HistoryEntry } from "../types";

interface Props {
  result?: ClassificationResponse | null;
  history?: HistoryEntry[];
}

export function ExportButtons({ result, history }: Props) {
  const hasResult = !!result;
  const hasHistory = !!history && history.length > 0;

  if (!hasResult && !hasHistory) return null;

  return (
    <div className="flex gap-2 flex-wrap">
      {hasResult && (
        <button
          onClick={() => exportResultPdf(result)}
          className="flex items-center gap-1.5 px-4 py-2 text-xs font-medium rounded-lg transition-all border border-gray-200 dark:border-border hover:bg-gray-100 dark:hover:bg-card-hover text-zinc-500 dark:text-zinc-400"
        >
          <HiOutlineDocumentDownload className="text-sm" />
          Exportar PDF
        </button>
      )}
      {hasHistory && (
        <button
          onClick={() => exportHistoryCsv(history)}
          className="flex items-center gap-1.5 px-4 py-2 text-xs font-medium rounded-lg transition-all border border-gray-200 dark:border-border hover:bg-gray-100 dark:hover:bg-card-hover text-zinc-500 dark:text-zinc-400"
        >
          <HiOutlineTable className="text-sm" />
          Exportar CSV
        </button>
      )}
    </div>
  );
}
