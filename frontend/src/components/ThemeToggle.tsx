import { HiOutlineSun, HiOutlineMoon } from "react-icons/hi";
import { useTheme } from "../contexts/ThemeContext";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg bg-white/20 hover:bg-white/30 transition-all"
      aria-label={theme === "light" ? "Ativar modo escuro" : "Ativar modo claro"}
    >
      {theme === "light" ? (
        <HiOutlineMoon className="text-xl text-white" />
      ) : (
        <HiOutlineSun className="text-xl text-yellow-200" />
      )}
    </button>
  );
}
