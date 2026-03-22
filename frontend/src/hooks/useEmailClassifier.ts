import { useState } from "react";
import type { ClassificationResponse, Provider } from "../types";
import { classifyText, classifyFile } from "../services/api";

interface Options {
  onSuccess?: (result: ClassificationResponse) => void;
}

export function useEmailClassifier(options?: Options) {
  const [result, setResult] = useState<ClassificationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reset = () => {
    setResult(null);
    setError(null);
  };

  const handleClassifyText = async (text: string, provider: Provider = "claude") => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await classifyText(text, provider);
      setResult(data);
      options?.onSuccess?.(data);
    } catch (err: unknown) {
      if (err && typeof err === "object" && "response" in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setError(
          axiosErr.response?.data?.detail || "Erro ao classificar o email."
        );
      } else {
        setError("Erro de conexão com o servidor.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClassifyFile = async (file: File, provider: Provider = "claude") => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await classifyFile(file, provider);
      setResult(data);
      options?.onSuccess?.(data);
    } catch (err: unknown) {
      if (err && typeof err === "object" && "response" in err) {
        const axiosErr = err as { response?: { data?: { detail?: string } } };
        setError(
          axiosErr.response?.data?.detail || "Erro ao classificar o arquivo."
        );
      } else {
        setError("Erro de conexão com o servidor.");
      }
    } finally {
      setLoading(false);
    }
  };

  return {
    result,
    setResult,
    loading,
    error,
    reset,
    classifyText: handleClassifyText,
    classifyFile: handleClassifyFile,
  };
}
