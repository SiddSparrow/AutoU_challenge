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
    <div className="bg-white dark:bg-card rounded-2xl border border-gray-200 dark:border-border p-6 space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-zinc-500 uppercase tracking-wider">
          Resposta Sugerida
        </h3>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all border border-gray-200 dark:border-border hover:bg-gray-100 dark:hover:bg-card-hover text-zinc-500 dark:text-zinc-400"
        >
          {copied ? (
            <>
              <HiOutlineCheck className="text-emerald-500" />
              Copiado!
            </>
          ) : (
            <>
              <HiOutlineClipboardCopy />
              Copiar
            </>
          )}
        </button>
      </div>

      <div className="bg-accent/5 border border-accent/10 rounded-xl p-4">
        <p className="text-gray-700 dark:text-zinc-200 text-sm whitespace-pre-wrap leading-relaxed">
          {response}
        </p>
      </div>
    </div>
  );
}
