import { useState, useRef, type DragEvent } from "react";
import { HiOutlineUpload, HiOutlineDocumentText } from "react-icons/hi";
import type { InputMode } from "../types";

interface Props {
  onSubmitText: (text: string) => void;
  onSubmitFile: (file: File) => void;
  loading: boolean;
}

const ACCEPTED_TYPES = [
  "text/plain",
  "application/pdf",
];

export function EmailUploader({ onSubmitText, onSubmitFile, loading }: Props) {
  const [mode, setMode] = useState<InputMode>("text");
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped && ACCEPTED_TYPES.includes(dropped.type)) {
      setFile(dropped);
    }
  };

  const handleSubmit = () => {
    if (mode === "text" && text.trim().length >= 10) {
      onSubmitText(text.trim());
    } else if (mode === "file" && file) {
      onSubmitFile(file);
    }
  };

  const isValid =
    (mode === "text" && text.trim().length >= 10) ||
    (mode === "file" && file !== null);

  return (
    <div className="bg-white dark:bg-card rounded-2xl border border-gray-200 dark:border-border p-6 space-y-5">
      {/* Mode Toggle */}
      <div className="flex gap-1 bg-gray-100 dark:bg-base p-1 rounded-xl w-fit">
        <button
          onClick={() => setMode("text")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            mode === "text"
              ? "bg-white dark:bg-card text-accent shadow-sm"
              : "text-gray-500 dark:text-zinc-500 hover:text-gray-700 dark:hover:text-zinc-300"
          }`}
        >
          <HiOutlineDocumentText className="inline mr-1.5 -mt-0.5" />
          Colar Texto
        </button>
        <button
          onClick={() => setMode("file")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            mode === "file"
              ? "bg-white dark:bg-card text-accent shadow-sm"
              : "text-gray-500 dark:text-zinc-500 hover:text-gray-700 dark:hover:text-zinc-300"
          }`}
        >
          <HiOutlineUpload className="inline mr-1.5 -mt-0.5" />
          Upload Arquivo
        </button>
      </div>

      {/* Text Input */}
      {mode === "text" && (
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Cole o conteúdo do email aqui..."
          className="w-full h-48 p-4 border border-gray-200 dark:border-border rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent/50 bg-white dark:bg-base text-gray-700 dark:text-zinc-200 placeholder-gray-400 dark:placeholder-zinc-600 transition-colors"
        />
      )}

      {/* File Upload */}
      {mode === "file" && (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`h-48 border-2 border-dashed rounded-xl flex flex-col items-center justify-center cursor-pointer transition-all ${
            dragOver
              ? "border-accent bg-accent/5"
              : file
                ? "border-emerald-500/50 bg-emerald-500/5"
                : "border-gray-300 dark:border-border hover:border-accent/50 hover:bg-gray-50 dark:hover:bg-card-hover"
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.pdf"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) setFile(f);
            }}
          />
          {file ? (
            <>
              <HiOutlineDocumentText className="text-4xl text-emerald-500 mb-2" />
              <p className="text-sm font-medium text-emerald-400">{file.name}</p>
              <p className="text-xs text-emerald-500/70 mt-1">
                Clique para trocar o arquivo
              </p>
            </>
          ) : (
            <>
              <HiOutlineUpload className="text-4xl text-zinc-500 dark:text-zinc-600 mb-2" />
              <p className="text-sm text-gray-500 dark:text-zinc-400">
                Arraste um arquivo .txt ou .pdf aqui
              </p>
              <p className="text-xs text-gray-400 dark:text-zinc-600 mt-1">
                ou clique para selecionar
              </p>
            </>
          )}
        </div>
      )}

      {/* Submit */}
      <button
        onClick={handleSubmit}
        disabled={!isValid || loading}
        className="w-full py-3 bg-accent hover:bg-accent-dark text-white font-semibold rounded-xl transition-all disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <svg
              className="animate-spin h-5 w-5"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            Classificando...
          </span>
        ) : (
          mode === "text" ? "Classificar Texto" : "Classificar Arquivo"
        )}
      </button>
    </div>
  );
}
