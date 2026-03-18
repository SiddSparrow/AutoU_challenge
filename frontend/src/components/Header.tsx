import { HiOutlineMail } from "react-icons/hi";

export function Header() {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white py-8 px-6 shadow-lg">
      <div className="max-w-4xl mx-auto flex items-center gap-4">
        <div className="bg-white/20 p-3 rounded-xl">
          <HiOutlineMail className="text-3xl" />
        </div>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Email Classifier
          </h1>
          <p className="text-blue-100 text-sm mt-1">
            Classificação inteligente de emails com IA
          </p>
        </div>
      </div>
    </header>
  );
}
