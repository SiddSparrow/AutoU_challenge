import { useState } from "react";
import { HiOutlineClipboardCopy, HiOutlineCheck } from "react-icons/hi";

interface Props {
  response: string;
}

export function ResponseSuggestion({ response }: Props) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(response);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white dark:bg-card rounded-xl border border-gray-200 dark:border-border p-5 space-y-3 animate-fade-in transition-colors">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium text-zinc-400 uppercase tracking-widest">
          Resposta Sugerida
        </p>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-md border border-gray-200 dark:border-border hover:bg-gray-100 dark:hover:bg-card-hover text-zinc-500 dark:text-zinc-400 transition-all duration-200"
        >
          {copied ? (
            <>
              <HiOutlineCheck className="text-emerald-500 text-sm" />
              <span className="text-emerald-500">Copiado</span>
            </>
          ) : (
            <>
              <HiOutlineClipboardCopy className="text-sm" />
              Copiar
            </>
          )}
        </button>
      </div>

      <div className="border-l-2 border-accent/30 pl-3">
        <p className="text-sm text-gray-700 dark:text-zinc-300 whitespace-pre-wrap leading-relaxed">
          {response}
        </p>
      </div>
    </div>
  );
}
