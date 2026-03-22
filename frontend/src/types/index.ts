export type Provider = "claude" | "classic" | "huggingface";

export type EmailTag =
  | "SPAM"
  | "POSSÍVEL GOLPE"
  | "URGENTE"
  | "SOLICITAÇÃO"
  | "RECLAMAÇÃO"
  | "REUNIÃO"
  | "INFORMATIVO"
  | "NÃO IMPORTANTE";

export interface ClassificationResponse {
  category: "Produtivo" | "Improdutivo";
  tag: EmailTag;
  suggested_response: string;
  summary: string;
  original_text: string;
}

export interface HistoryEntry extends ClassificationResponse {
  id: string;
  timestamp: string;
}

export type InputMode = "text" | "file";
