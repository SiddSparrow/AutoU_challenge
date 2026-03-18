import { Toaster } from "react-hot-toast";
import { Header } from "./components/Header";
import { EmailUploader } from "./components/EmailUploader";
import { ResultCard } from "./components/ResultCard";
import { ResponseSuggestion } from "./components/ResponseSuggestion";
import { useEmailClassifier } from "./hooks/useEmailClassifier";

function App() {
  const { result, loading, error, classifyText, classifyFile } =
    useEmailClassifier();

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      <Header />

      <main className="max-w-2xl mx-auto px-4 py-10 space-y-6">
        <EmailUploader
          onSubmitText={classifyText}
          onSubmitFile={classifyFile}
          loading={loading}
        />

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 text-sm">
            {error}
          </div>
        )}

        {result && (
          <>
            <ResultCard result={result} />
            <ResponseSuggestion response={result.suggested_response} />
          </>
        )}
      </main>

      <footer className="text-center py-6 text-xs text-gray-400">
        Email Classifier &mdash; Powered by Claude AI
      </footer>
    </div>
  );
}

export default App;
