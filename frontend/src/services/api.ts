import axios from "axios";
import type { ClassificationResponse, Provider } from "../types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "https://autouchallenge-production.up.railway.app",
});
 
export async function classifyText(
  text: string,
  provider: Provider = "claude"
): Promise<ClassificationResponse> {
  const { data } = await api.post<ClassificationResponse>(
    "/api/classify/text",
    { text, provider }
  );
  return data;
}

export async function classifyFile(
  file: File,
  provider: Provider = "claude"
): Promise<ClassificationResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<ClassificationResponse>(
    `/api/classify/file?provider=${provider}`,
    formData
  );
  return data;
}
