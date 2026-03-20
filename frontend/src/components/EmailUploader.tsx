import { useState, useRef, type DragEvent } from "react";
import { HiOutlineUpload, HiOutlineDocumentText } from "react-icons/hi";
import type { InputMode } from "../types";

interface Props {
  onSubmitText: (text: string) => void;
  onSubmitFile: (file: File) => void;
  loading: boolean;
}

const ACCEPTED_TYPES = ["text/plain", "application/pdf"];

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
    <div className="bg-white dark:bg-black rounded-xl border border-slate-200 dark:border-border p-5 space-y-4 transition-colors">
      {/* Mode Toggle */}
      <div className="flex gap-0.5 bg-slate-100 dark:bg-base p-0.5 rounded-lg w-fit border border-slate-200 dark:border-border">
        {(["text", "file"] as InputMode[]).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-md text-xs font-medium transition-all duration-200 ${
              mode === m
                ? "bg-white dark:bg-black text-slate-800 dark:text-zinc-100 shadow-sm"
                : "text-slate-500 dark:text-zinc-500 hover:text-slate-700 dark:hover:text-zinc-300"
            }`}
          >
            {m === "text" ? (
              <>
                <HiOutlineDocumentText className="text-sm" />
                Colar Texto
              </>
            ) : (
              <>
                <HiOutlineUpload className="text-sm" />
                Upload Arquivo
              </>
            )}
          </button>
        ))}
      </div>

      {/* Text Input */}
      {mode === "text" && (
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Cole o conteúdo do email aqui..."
          className="w-full h-44 p-3.5 border border-slate-200 dark:border-border rounded-lg resize-none text-sm leading-relaxed focus:outline-none focus:ring-1 focus:ring-accent/40 focus:border-accent/40 bg-white dark:bg-base text-slate-700 dark:text-zinc-200 placeholder-slate-400 dark:placeholder-zinc-600 transition-all"
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
          className={`h-44 border border-dashed rounded-lg flex flex-col items-center justify-center cursor-pointer transition-all duration-200 ${
            dragOver
              ? "border-accent/60 bg-accent/5"
              : file
                ? "border-emerald-500/40 bg-emerald-500/5"
                : "border-slate-300 dark:border-border hover:border-accent/40 hover:bg-slate-50 dark:hover:bg-base"
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
              <HiOutlineDocumentText className="text-3xl text-emerald-500 mb-2" />
              <p className="text-sm font-medium text-emerald-400">{file.name}</p>
              <p className="text-xs text-zinc-500 mt-1">Clique para trocar</p>
            </>
          ) : (
            <>
              <HiOutlineUpload className="text-3xl text-zinc-500 mb-2" />
              <p className="text-sm text-slate-500 dark:text-zinc-400">
                Arraste um arquivo .txt ou .pdf
              </p>
              <p className="text-xs text-slate-400 dark:text-zinc-600 mt-1">
                ou clique para selecionar
              </p>
            </>
          )}
        </div>
      )}

      {/* Submit — outlined ghost style */}
      <button
        onClick={handleSubmit}
        disabled={!isValid || loading}
        className="w-full py-2.5 rounded-lg text-sm font-medium transition-all duration-200 border border-accent/30 text-accent hover:bg-accent/8 hover:border-accent/50 focus:outline-none focus:ring-1 focus:ring-accent/30 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent disabled:hover:border-accent/30"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
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
        ) : mode === "text" ? (
          "Classificar Texto"
        ) : (
          "Classificar Arquivo"
        )}
      </button>
    </div>
  );
}
