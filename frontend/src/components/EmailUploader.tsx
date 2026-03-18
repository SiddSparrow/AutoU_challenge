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
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-md border border-gray-100 dark:border-gray-700 p-6 space-y-5">
      {/* Mode Toggle */}
      <div className="flex gap-2 bg-gray-100 dark:bg-gray-700 p-1 rounded-xl w-fit">
        <button
          onClick={() => setMode("text")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            mode === "text"
              ? "bg-white dark:bg-gray-600 text-blue-700 dark:text-blue-300 shadow-sm"
              : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
          }`}
        >
          <HiOutlineDocumentText className="inline mr-1.5 -mt-0.5" />
          Colar Texto
        </button>
        <button
          onClick={() => setMode("file")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            mode === "file"
              ? "bg-white dark:bg-gray-600 text-blue-700 dark:text-blue-300 shadow-sm"
              : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
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
          className="w-full h-48 p-4 border border-gray-200 dark:border-gray-600 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500"
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
              ? "border-blue-500 bg-blue-50 dark:bg-blue-900/30"
              : file
                ? "border-green-400 bg-green-50 dark:bg-green-900/20"
                : "border-gray-300 dark:border-gray-600 hover:border-blue-400 hover:bg-gray-50 dark:hover:bg-gray-700"
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
              <HiOutlineDocumentText className="text-4xl text-green-500 mb-2" />
              <p className="text-sm font-medium text-green-700 dark:text-green-400">{file.name}</p>
              <p className="text-xs text-green-500 dark:text-green-500 mt-1">
                Clique para trocar o arquivo
              </p>
            </>
          ) : (
            <>
              <HiOutlineUpload className="text-4xl text-gray-400 dark:text-gray-500 mb-2" />
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Arraste um arquivo .txt ou .pdf aqui
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
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
        className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
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
          "Classificar Email"
        )}
      </button>
    </div>
  );
}
