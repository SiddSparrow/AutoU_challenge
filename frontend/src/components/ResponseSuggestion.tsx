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
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-md border border-gray-100 dark:border-gray-700 p-6 space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
          Resposta Sugerida
        </h3>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300"
        >
          {copied ? (
            <>
              <HiOutlineCheck className="text-green-500" />
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

      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded-xl p-4">
        <p className="text-gray-700 dark:text-gray-200 text-sm whitespace-pre-wrap leading-relaxed">
          {response}
        </p>
      </div>
    </div>
  );
}
