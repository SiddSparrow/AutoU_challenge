import type { HistoryEntry } from "../types";

export function exportHistoryCsv(history: HistoryEntry[]) {
  const header = "Data,Categoria,Confianca,Resumo,Resposta Sugerida\n";

  const rows = history
    .map((entry) => {
      const date = new Date(entry.timestamp).toLocaleString("pt-BR");
      const confidence = Math.round(entry.confidence * 100) + "%";
      const summary = csvEscape(entry.summary);
      const response = csvEscape(entry.suggested_response);
      return `${date},${entry.category},${confidence},${summary},${response}`;
    })
    .join("\n");

  const bom = "\uFEFF";
  const blob = new Blob([bom + header + rows], {
    type: "text/csv;charset=utf-8;",
  });

  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `historico-classificacoes-${Date.now()}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

function csvEscape(value: string): string {
  const escaped = value.replace(/"/g, '""');
  return `"${escaped}"`;
}
