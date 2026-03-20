import { useState } from "react";
import { Toaster } from "react-hot-toast";
import { ThemeProvider } from "./contexts/ThemeContext";
import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { MiniStatsBar } from "./components/MiniStatsBar";
import { EmailUploader } from "./components/EmailUploader";
import { ResultCard } from "./components/ResultCard";
import { ResponseSuggestion } from "./components/ResponseSuggestion";
import { History } from "./components/History";
import { StatsCards } from "./components/StatsCards";
import { useEmailClassifier } from "./hooks/useEmailClassifier";
import { useClassificationHistory } from "./hooks/useClassificationHistory";
import type { View } from "./components/Sidebar";
import type { HistoryEntry } from "./types";

const viewMeta: Record<View, { title: string; subtitle: string }> = {
  classify: {
    title: "Classificar Email",
    subtitle: "Analise e classifique emails com IA",
  },
  history: {
    title: "Histórico",
    subtitle: "Classificações realizadas nesta sessão",
  },
  stats: {
    title: "Gráfico",
    subtitle: "Volume de emails e distribuição por tags",
  },
};

function AppContent() {
  const [activeView, setActiveView] = useState<View>("classify");
  const { history, addEntry, clearHistory } = useClassificationHistory();
  const { result, setResult, loading, error, classifyText, classifyFile } =
    useEmailClassifier({ onSuccess: addEntry });

  const handleSelectHistory = (entry: HistoryEntry) => {
    setResult(entry);
    setActiveView("classify");
  };

  const { title, subtitle } = viewMeta[activeView];

  return (
    <div className="flex h-screen bg-[#f0f2f8] dark:bg-base overflow-hidden transition-colors">
      <Toaster
        position="top-right"
        toastOptions={{
          className: "dark:!bg-[#12121a] dark:!text-[#f1f1f5] dark:!border-[#1e1e2e] !bg-white !text-slate-800 !border-slate-200 !shadow-sm !text-sm",
        }}
      />

      <Sidebar activeView={activeView} onNavigate={setActiveView} />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header title={title} subtitle={subtitle} activeView={activeView} onNavigate={setActiveView} />

        <MiniStatsBar history={history} result={result} />

        <main className="flex-1 overflow-y-auto p-4 sm:p-6">
          {/* ── Classify view ── */}
          {activeView === "classify" && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
              {/* Left: uploader */}
              <div className="space-y-4">
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
              </div>

              {/* Right: result (only when exists) */}
              {result && (
                <div className="space-y-4 animate-slide-up">
                  <ResultCard result={result} />
                  <ResponseSuggestion response={result.suggested_response} />
                </div>
              )}
            </div>
          )}

          {/* ── History view ── */}
          {activeView === "history" && (
            <History
              history={history}
              onClear={clearHistory}
              onSelect={handleSelectHistory}
            />
          )}

          {/* ── Stats / Chart view ── */}
          {activeView === "stats" && <StatsCards history={history} onSelectEntry={handleSelectHistory} />}
        </main>
      </div>
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
