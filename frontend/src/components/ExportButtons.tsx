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
          className="flex items-center gap-1.5 px-4 py-2 text-xs font-medium rounded-lg transition-all bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/40 text-blue-600 dark:text-blue-400"
        >
          <HiOutlineDocumentDownload className="text-sm" />
          Exportar PDF
        </button>
      )}
      {hasHistory && (
        <button
          onClick={() => exportHistoryCsv(history)}
          className="flex items-center gap-1.5 px-4 py-2 text-xs font-medium rounded-lg transition-all bg-emerald-50 dark:bg-emerald-900/20 hover:bg-emerald-100 dark:hover:bg-emerald-900/40 text-emerald-600 dark:text-emerald-400"
        >
          <HiOutlineTable className="text-sm" />
          Exportar CSV
        </button>
      )}
    </div>
  );
}
