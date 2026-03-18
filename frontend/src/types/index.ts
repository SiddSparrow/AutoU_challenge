export interface ClassificationResponse {
  category: "Produtivo" | "Improdutivo";
  confidence: number;
  suggested_response: string;
  summary: string;
  original_text: string;
}

export type InputMode = "text" | "file";
