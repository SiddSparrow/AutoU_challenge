import { jsPDF } from "jspdf";
import type { ClassificationResponse } from "../types";

export function exportResultPdf(result: ClassificationResponse) {
  const doc = new jsPDF();
  const margin = 20;
  let y = margin;

  // Title
  doc.setFontSize(18);
  doc.setFont("helvetica", "bold");
  doc.text("Email Classifier - Resultado", margin, y);
  y += 12;

  // Date
  doc.setFontSize(9);
  doc.setFont("helvetica", "normal");
  doc.setTextColor(120);
  doc.text(`Gerado em: ${new Date().toLocaleString("pt-BR")}`, margin, y);
  y += 14;

  // Classification
  doc.setTextColor(0);
  doc.setFontSize(12);
  doc.setFont("helvetica", "bold");
  doc.text("Classificacao", margin, y);
  y += 8;

  doc.setFontSize(11);
  doc.setFont("helvetica", "normal");
  doc.text(`Categoria: ${result.category}`, margin, y);
  y += 7;
  doc.text(`Tag: ${result.tag}`, margin, y);
  y += 12;

  // Summary
  doc.setFont("helvetica", "bold");
  doc.setFontSize(12);
  doc.text("Resumo", margin, y);
  y += 8;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  const summaryLines = doc.splitTextToSize(result.summary, 170);
  doc.text(summaryLines, margin, y);
  y += summaryLines.length * 5 + 10;

  // Suggested Response
  doc.setFont("helvetica", "bold");
  doc.setFontSize(12);
  doc.text("Resposta Sugerida", margin, y);
  y += 8;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  const responseLines = doc.splitTextToSize(result.suggested_response, 170);
  doc.text(responseLines, margin, y);
  y += responseLines.length * 5 + 10;

  // Original Email
  doc.setFont("helvetica", "bold");
  doc.setFontSize(12);
  doc.text("Email Original", margin, y);
  y += 8;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  doc.setTextColor(80);
  const emailLines = doc.splitTextToSize(result.original_text, 170);
  // Limit to avoid going past page
  const maxLines = Math.min(emailLines.length, 40);
  doc.text(emailLines.slice(0, maxLines), margin, y);

  doc.save(`classificacao-${result.category.toLowerCase()}-${Date.now()}.pdf`);
}
