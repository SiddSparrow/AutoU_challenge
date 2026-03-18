import { HiOutlineMail } from "react-icons/hi";
import { ThemeToggle } from "./ThemeToggle";

export function Header() {
  return (
    <header className="bg-white dark:bg-base border-b border-gray-200 dark:border-border py-5 px-6 transition-colors">
      <div className="max-w-5xl mx-auto flex items-center gap-4">
        <div className="bg-accent/10 p-2.5 rounded-xl">
          <HiOutlineMail className="text-2xl text-accent" />
        </div>
        <div className="flex-1">
          <h1 className="text-xl font-bold tracking-tight text-gray-900 dark:text-zinc-100">
            Email Classifier
          </h1>
          <p className="text-zinc-400 dark:text-zinc-500 text-xs mt-0.5">
            Classificação inteligente de emails com IA
          </p>
        </div>
        <ThemeToggle />
      </div>
    </header>
  );
}
