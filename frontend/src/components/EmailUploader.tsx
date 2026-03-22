import { useState, useRef, type DragEvent } from "react";
import { HiOutlineUpload, HiOutlineDocumentText, HiOutlineSparkles, HiOutlineChip } from "react-icons/hi";
import type { InputMode, Provider } from "../types";

interface Props {
  onSubmitText: (text: string, provider: Provider) => void;
  onSubmitFile: (file: File, provider: Provider) => void;
  loading: boolean;
}

const ACCEPTED_TYPES = ["text/plain", "application/pdf"];

const PROVIDERS: { value: Provider; label: string; description: string }[] = [
  { value: "claude", label: "Claude API", description: "IA generativa (Anthropic)" },
  { value: "classic", label: "Classic NLP", description: "TF-IDF + Regressão Logística" },
  { value: "huggingface", label: "HuggingFace", description: "Zero-shot (XLM-RoBERTa)" },
];

export function EmailUploader({ onSubmitText, onSubmitFile, loading }: Props) {
  const [mode, setMode] = useState<InputMode>("text");
  const [provider, setProvider] = useState<Provider>("claude");
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
      onSubmitText(text.trim(), provider);
    } else if (mode === "file" && file) {
      onSubmitFile(file, provider);
    }
  };

  const isValid =
    (mode === "text" && text.trim().length >= 10) ||
    (mode === "file" && file !== null);

  return (
    <div className="bg-white dark:bg-black rounded-xl border border-slate-200 dark:border-border p-5 space-y-4 transition-colors">
      {/* Input mode toggle */}
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

      {/* Provider toggle */}
      <div className="space-y-1.5">
        <p className="text-[10px] font-medium text-zinc-500 uppercase tracking-widest">
          Classificador
        </p>
        <div className="grid grid-cols-2 gap-2">
          {PROVIDERS.map((p) => (
            <button
              key={p.value}
              onClick={() => setProvider(p.value)}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-left transition-all duration-200 ${
                provider === p.value
                  ? "border-violet-500/40 bg-violet-500/8 text-violet-400"
                  : "border-slate-200 dark:border-border text-slate-500 dark:text-zinc-500 hover:border-slate-300 dark:hover:border-zinc-600"
              }`}
            >
              {p.value === "claude" ? (
                <HiOutlineSparkles className="text-base shrink-0" />
              ) : (
                <HiOutlineChip className="text-base shrink-0" />
              )}
              <div className="min-w-0">
                <p className="text-xs font-semibold leading-none">{p.label}</p>
                <p className="text-[10px] leading-none mt-0.5 opacity-70 truncate">
                  {p.description}
                </p>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Submit */}
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
