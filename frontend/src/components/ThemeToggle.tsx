import { HiOutlineSun, HiOutlineMoon } from "react-icons/hi";
import { useTheme } from "../contexts/ThemeContext";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="p-1.5 rounded-lg border border-gray-200 dark:border-border hover:bg-gray-100 dark:hover:bg-card-hover text-zinc-500 dark:text-zinc-400 hover:text-gray-800 dark:hover:text-zinc-200 transition-all duration-200"
      aria-label={theme === "light" ? "Ativar modo escuro" : "Ativar modo claro"}
    >
      {theme === "light" ? (
        <HiOutlineMoon className="text-base" />
      ) : (
        <HiOutlineSun className="text-gray-300" />
      )}
    </button>
  );
}
