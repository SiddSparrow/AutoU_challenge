import {
  HiOutlineMail,
  HiOutlineClock,
  HiOutlinePresentationChartLine,
} from "react-icons/hi";

export type View = "classify" | "history" | "stats";

const navItems: { id: View; label: string; icon: React.ElementType }[] = [
  { id: "classify", label: "Classificar", icon: HiOutlineMail },
  { id: "history", label: "Histórico", icon: HiOutlineClock },
  { id: "stats", label: "Gráfico", icon: HiOutlinePresentationChartLine },
];

interface Props {
  activeView: View;
  onNavigate: (view: View) => void;
}

export function Sidebar({ activeView, onNavigate }: Props) {
  return (
    <aside className="hidden lg:flex w-52 shrink-0 flex-col bg-gray-50 dark:bg-black border-r border-gray-200 dark:border-border transition-colors">
      {/* Brand */}
      <div className="px-5 py-5">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg border border-accent/20 bg-accent/5">
            <HiOutlineMail className="text-lg text-zinc-500 dark:text-accent " />
          </div>
          <div className="leading-tight">
            <p className="text-sm font-medium text-gray-900 dark:text-zinc-100">
              Email
            </p>
            <p className="text-xs text-zinc-500">Classifier</p>
          </div>
        </div>
      </div>

      <div className="h-px bg-gray-200 dark:bg-border mx-5" />

      {/* Nav */}
      <nav className="flex-1 px-2.5 py-4 space-y-0.5">
        {navItems.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onNavigate(id)}
            className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-all duration-200 text-left ${
              activeView === id
                ? " bg-gray-100 dark:bg-gray-950 dark:text-white text-zinc-700 font-bold border border-accent/15"
                : "text-zinc-500 dark:text-zinc-300 hover:text-gray-900 dark:hover:text-zinc-200 hover:bg-gray-100 dark:hover:bg-card-hover border border-transparent"
            }`}
          >
            <Icon
              className={`text-base dark:text-zinc-100 shrink-0 ${
                activeView === id ? "font-bold" : ""
              }`}
            />
            <span className="font-medium">{label}</span>
          </button>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-gray-200 dark:border-border">
        <p className="text-xs text-zinc-600 dark:text-zinc-600">
          Desafio Técnico &mdash; AutoU
        </p>
      </div>
    </aside>
  );
}
