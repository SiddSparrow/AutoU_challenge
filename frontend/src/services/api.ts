import axios from "axios";
import type { ClassificationResponse } from "../types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "",
});

export async function classifyText(
  text: string
): Promise<ClassificationResponse> {
  const { data } = await api.post<ClassificationResponse>(
    "/api/classify/text",
    { text }
  );
  return data;
}

export async function classifyFile(
  file: File
): Promise<ClassificationResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<ClassificationResponse>(
    "/api/classify/file",
    formData
  );
  return data;
}
