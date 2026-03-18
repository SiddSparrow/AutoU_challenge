import { Toaster } from "react-hot-toast";
import { ThemeProvider } from "./contexts/ThemeContext";
import { Header } from "./components/Header";
import { EmailUploader } from "./components/EmailUploader";
import { ResultCard } from "./components/ResultCard";
import { ResponseSuggestion } from "./components/ResponseSuggestion";
import { History } from "./components/History";
import { StatsCards } from "./components/StatsCards";
import { ExportButtons } from "./components/ExportButtons";
import { useEmailClassifier } from "./hooks/useEmailClassifier";
import { useClassificationHistory } from "./hooks/useClassificationHistory";
import type { HistoryEntry } from "./types";

function AppContent() {
  const { history, addEntry, clearHistory } = useClassificationHistory();

  const { result, setResult, loading, error, classifyText, classifyFile } =
    useEmailClassifier({ onSuccess: addEntry });

  const handleSelectHistory = (entry: HistoryEntry) => {
    setResult(entry);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      <Toaster position="top-right" />
      <Header />

      <main className="max-w-2xl mx-auto px-4 py-10 space-y-6">
        <EmailUploader
          onSubmitText={classifyText}
          onSubmitFile={classifyFile}
          loading={loading}
        />

        {error && (
          <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 rounded-xl p-4 text-sm">
            {error}
          </div>
        )}

        {result && (
          <>
            <ResultCard result={result} />
            <ResponseSuggestion response={result.suggested_response} />
            <ExportButtons result={result} history={history} />
          </>
        )}

        <StatsCards history={history} />

        <History
          history={history}
          onClear={clearHistory}
          onSelect={handleSelectHistory}
        />
      </main>

      <footer className="text-center py-6 text-xs text-gray-400 dark:text-gray-500">
        Desafio Técnico &mdash; AutoU 
      </footer>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;
