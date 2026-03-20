import { useState, useRef, useEffect } from "react";
import {
  HiOutlineMenu,
  HiOutlineX,
  HiOutlineMail,
  HiOutlineClock,
  HiOutlinePresentationChartLine,
} from "react-icons/hi";
import { ThemeToggle } from "./ThemeToggle";
import type { View } from "./Sidebar";

const navItems: { id: View; label: string; icon: React.ElementType }[] = [
  { id: "classify", label: "Classificar", icon: HiOutlineMail },
  { id: "history", label: "Histórico", icon: HiOutlineClock },
  { id: "stats", label: "Gráfico", icon: HiOutlinePresentationChartLine },
];

interface Props {
  title: string;
  subtitle?: string;
  activeView: View;
  onNavigate: (view: View) => void;
}

export function Header({ title, subtitle, activeView, onNavigate }: Props) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    if (!mobileOpen) return;
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMobileOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [mobileOpen]);

  const handleNavigate = (view: View) => {
    onNavigate(view);
    setMobileOpen(false);
  };

  return (
    <header className="shrink-0 flex items-center justify-between px-4 sm:px-6 py-3.5 bg-gray-50 dark:bg-black border-b border-slate-200 dark:border-border transition-colors relative z-30">
      <div className="flex items-center gap-3">
        {/* Hamburger — only on mobile */}
        <div ref={menuRef} className="relative lg:hidden">
          <button
            onClick={() => setMobileOpen((o) => !o)}
            className="p-1.5 rounded-lg border border-slate-200 dark:border-border hover:bg-slate-50 dark:hover:bg-card-hover text-slate-500 dark:text-zinc-400 transition-all duration-200"
            aria-label="Abrir menu"
          >
            {mobileOpen ? (
              <HiOutlineX className="text-[1rem]" />
            ) : (
              <HiOutlineMenu className="text-[1rem]" />
            )}
          </button>

          {/* Dropdown */}
          {mobileOpen && (
            <div className="absolute top-full left-0 mt-2 w-48 bg-gray-50 dark:bg-black border border-slate-200 dark:border-border rounded-xl shadow-lg overflow-hidden animate-fade-in">
              {navItems.map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => handleNavigate(id)}
                  className={`w-full flex items-center gap-2.5 px-4 py-2.5 text-sm transition-all duration-150 text-left ${
                    activeView === id
                      ? " bg-gray-100 dark:bg-gray-950 dark:text-white text-zinc-700 font-bold border border-accent/15"
                : "text-zinc-500 dark:text-zinc-300 hover:text-gray-900 dark:hover:text-zinc-200 hover:bg-gray-100 dark:hover:bg-card-hover border border-transparent"
                  }`}
                >
                  <Icon className="text-base shrink-0" />
                  <span className="font-medium">{label}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        <div>
          <h1 className="text-[1rem] font-medium text-slate-800 dark:text-zinc-100 tracking-tight leading-tight">
            {title}
          </h1>
          {subtitle && (
            <p className="text-xs text-zinc-500 mt-0.5 hidden sm:block">
              {subtitle}
            </p>
          )}
        </div>
      </div>

      <ThemeToggle />
    </header>
  );
}
