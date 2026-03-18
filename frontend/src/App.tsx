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
    <div className="min-h-screen bg-gray-50 dark:bg-base transition-colors">
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "#12121a",
            color: "#f1f1f5",
            border: "1px solid #1e1e2e",
          },
        }}
      />
      <Header />

      <main className="max-w-5xl mx-auto px-6 py-10 space-y-6">
        <EmailUploader
          onSubmitText={classifyText}
          onSubmitFile={classifyFile}
          loading={loading}
        />

        {error && (
          <div className="bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 text-red-700 dark:text-red-400 rounded-2xl p-4 text-sm animate-fade-in">
            {error}
          </div>
        )}

        {result && (
          <div className="space-y-6 animate-slide-up">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ResultCard result={result} />
              <ResponseSuggestion response={result.suggested_response} />
            </div>
            <ExportButtons result={result} history={history} />
          </div>
        )}

        <StatsCards history={history} />

        <History
          history={history}
          onClear={clearHistory}
          onSelect={handleSelectHistory}
        />
      </main>

      <footer className="text-center py-8 text-xs text-zinc-500 dark:text-zinc-600">
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
