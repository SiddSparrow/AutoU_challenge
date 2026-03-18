export interface ClassificationResponse {
  category: "Produtivo" | "Improdutivo";
  confidence: number;
  suggested_response: string;
  summary: string;
  original_text: string;
}

export interface HistoryEntry extends ClassificationResponse {
  id: string;
  timestamp: string;
}

export type InputMode = "text" | "file";
