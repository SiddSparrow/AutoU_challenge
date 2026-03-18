import { HiOutlineSun, HiOutlineMoon } from "react-icons/hi";
import { useTheme } from "../contexts/ThemeContext";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg border border-gray-200 dark:border-border hover:bg-gray-100 dark:hover:bg-card-hover transition-all"
      aria-label={theme === "light" ? "Ativar modo escuro" : "Ativar modo claro"}
    >
      {theme === "light" ? (
        <HiOutlineMoon className="text-lg text-zinc-600" />
      ) : (
        <HiOutlineSun className="text-lg text-zinc-400" />
      )}
    </button>
  );
}
