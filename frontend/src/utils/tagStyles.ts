import type { EmailTag } from "../types";

interface TagStyle {
  bg: string;
  text: string;
  border: string;
}

const TAG_STYLES: Record<string, TagStyle> = {
  "SPAM":            { bg: "bg-amber-500/10",  text: "text-amber-400",  border: "border-amber-500/25" },
  "POSSÍVEL GOLPE":  { bg: "bg-red-500/10",    text: "text-red-400",    border: "border-red-500/25" },
  "URGENTE":         { bg: "bg-orange-500/10", text: "text-orange-400", border: "border-orange-500/25" },
  "SOLICITAÇÃO":     { bg: "bg-violet-500/10", text: "text-violet-400", border: "border-violet-500/25" },
  "RECLAMAÇÃO":      { bg: "bg-rose-500/10",   text: "text-rose-400",   border: "border-rose-500/25" },
  "REUNIÃO":         { bg: "bg-cyan-500/10",   text: "text-cyan-400",   border: "border-cyan-500/25" },
  "INFORMATIVO":     { bg: "bg-blue-500/10",   text: "text-blue-400",   border: "border-blue-500/25" },
  "NÃO IMPORTANTE":  { bg: "bg-zinc-500/10",   text: "text-zinc-400",   border: "border-zinc-500/25" },
};

const FALLBACK: TagStyle = { bg: "bg-zinc-500/10", text: "text-zinc-400", border: "border-zinc-500/25" };

export function getTagStyle(tag: EmailTag | string): TagStyle {
  return TAG_STYLES[tag] ?? FALLBACK;
}
