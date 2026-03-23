"""
Benchmark comparativo entre os 3 classificadores de email.
Executa cada caso de teste nos 3 modelos e gera um relatório Markdown versionado.

Uso:
    python benchmark.py
    python benchmark.py --note "Descrição das mudanças nesta versão"

Saída:
    benchmarks/v{N}_YYYY-MM-DD.md   — relatório desta execução
    BENCHMARK.md                    — sempre aponta para a versão mais recente
"""

import argparse
import asyncio
import glob
import json
import os
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import date

# ---------------------------------------------------------------------------
# Env setup — carrega .env antes de importar qualquer módulo da app
# ---------------------------------------------------------------------------
def _load_dotenv(path: str) -> None:
    """Minimal .env loader — sem dependência extra."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

_load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
os.environ.setdefault("HF_MODEL", "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
os.environ.setdefault("AI_MODEL", "claude-sonnet-4-20250514")

sys.path.insert(0, os.path.dirname(__file__))

from app.services.classifier.classic_nlp_classifier import ClassicNLPClassifier
from app.services.classifier.huggingface_classifier import HuggingFaceClassifier
from app.services.classifier.claude_classifier import ClaudeClassifier
from app.services.text_preprocessor import TextPreprocessor
from app.core.interfaces import ClassificationResult

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_BENCHMARKS_DIR = os.path.join(_REPO_ROOT, "benchmarks")
_LATEST_MD = os.path.join(_REPO_ROOT, "BENCHMARK.md")
_DATA_PATTERN = os.path.join(_BENCHMARKS_DIR, "v*_data.json")

# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

@dataclass
class TestCase:
    name: str
    expected_category: str
    expected_tag: str
    text: str

TEST_CASES: list[TestCase] = [
    TestCase("Reunião corporativa",          "Produtivo",   "REUNIÃO",
        "Convido para reunião de alinhamento do Q2 na próxima terça-feira, 25/03, às 10h, sala Inovação. "
        "Pauta: revisão de metas, definição de prioridades e alocação de recursos para os próximos 3 meses. "
        "Confirme presença até sexta-feira.\n\nAtenciosamente, Carlos Drummond — COO"),
    TestCase("Reclamação formal",            "Produtivo",   "RECLAMAÇÃO",
        "Registro formal de reclamação referente ao sistema de conciliação bancária que apresenta falhas "
        "desde a última atualização em 15/03. Já foram abertas 3 ocorrências (tickets #4421, #4435, #4489) "
        "sem resolução. Os erros estão causando impacto direto no fechamento contábil do mês. "
        "Exijo resposta e prazo de resolução até amanhã, 24/03, às 12h.\n\nRafael Souza — Controller"),
    TestCase("Spam promocional",             "Improdutivo", "SPAM",
        "OFERTA IMPERDÍVEL!!!\n\nSó até meia-noite de hoje: 70% de desconto em todos os cursos de finanças! "
        "Use o cupom FINANCEIRO70 e comece agora sua jornada rumo à liberdade financeira. "
        "Mais de 50.000 alunos já transformaram suas vidas. CLIQUE AQUI e garanta sua vaga!"),
    TestCase("Phishing bancário",            "Improdutivo", "POSSÍVEL GOLPE",
        "AVISO URGENTE DO SEU BANCO\n\nSua conta foi temporariamente suspensa por atividade suspeita. "
        "Para reativar o acesso, confirme seus dados clicando no link abaixo em até 24 horas. "
        "Caso não regularize, sua conta será encerrada definitivamente.\n\nhttp://bit.ly/banco-verificacao"),
    TestCase("Solicitação de suporte",       "Produtivo",   "SOLICITAÇÃO",
        "Olá equipe de TI, gostaria de solicitar acesso ao módulo de relatórios gerenciais do sistema ERP "
        "para a analista Fernanda Lima, recém-contratada no departamento de controladoria. "
        "O perfil de acesso necessário é o mesmo da analista Marina Costa. "
        "Aguardo confirmação de quando o acesso estará disponível.\n\nObrigado, João Mendes — Gerente"),
    TestCase("Email urgente",                "Produtivo",   "URGENTE",
        "CRÍTICO — AÇÃO IMEDIATA NECESSÁRIA\n\nO sistema de processamento de pagamentos está fora do ar "
        "desde as 14h32. Mais de 2.300 transações na fila sem processamento. Impacto direto na liquidação. "
        "SLA regulatório vence às 17h00. Precisamos da equipe de infraestrutura e do gestor de incidentes "
        "na sala de guerra agora.\n\nLucas Ferreira — Head de Operações"),
    TestCase("Comunicado informativo",       "Improdutivo", "INFORMATIVO",
        "Comunicado interno — TI\n\nInformamos que o ambiente de homologação estará indisponível neste "
        "sábado, 28/03, das 08h às 16h, para manutenção preventiva dos servidores e atualização do banco "
        "de dados. O ambiente de produção não será afetado. Em caso de dúvidas, contate o service desk "
        "pelo ramal 4000.\n\nEquipe de Infraestrutura"),
    TestCase("Boas-vindas / onboarding",     "Improdutivo", "INFORMATIVO",
        "Olá, Camila!\n\nÉ com grande satisfação que dou as boas-vindas à equipe de Engenharia da NovaTech. "
        "Seu onboarding está agendado para as 9h na sala Inovação, no terceiro andar. O Diego, nosso tech "
        "lead, vai acompanhar você no primeiro dia. Já providenciamos seu acesso ao GitLab, Slack e ao "
        "ambiente de desenvolvimento. Teremos um 1:1 na sexta para alinhar expectativas.\n\nAbração, Rafael"),
    TestCase("Agradecimento",                "Improdutivo", "NÃO IMPORTANTE",
        "Oi time,\n\nSó passando para agradecer pelo apoio de todos durante o fechamento do trimestre. "
        "Foi uma semana intensa mas conseguimos entregar tudo no prazo. Vocês são incríveis! "
        "Bom fim de semana a todos e descansem bastante.\n\nBeijos, Ana"),
    TestCase("Texto corrido (não email)",    "Improdutivo", "INFORMATIVO",
        "A taxa Selic passou por sucessivos ajustes ao longo de 2025, reflexo da política monetária "
        "adotada pelo Banco Central para conter a inflação dentro da meta estabelecida pelo CMN. "
        "Analistas projetam que os juros devem permanecer elevados até o segundo semestre de 2026, "
        "impactando o custo do crédito e os investimentos em renda variável."),
    TestCase("Email em inglês",              "Produtivo",   "SOLICITAÇÃO",
        "Hi support team,\n\nI'm reaching out regarding invoice #INV-2026-0892 issued on March 10th. "
        "The payment was processed on our end on March 15th (transaction ID: TXN-88821), "
        "but it still appears as pending in your system. Could you please investigate and confirm receipt?\n\n"
        "Best regards, Michael Thompson — Finance Director"),
    TestCase("Mensagem curta / low-info",    "Improdutivo", "NÃO IMPORTANTE",
        "ok, pode fechar o chamado"),
]

# ---------------------------------------------------------------------------
# Versioning helpers
# ---------------------------------------------------------------------------

def _next_version() -> int:
    """Return the next version number based on existing data files."""
    existing = glob.glob(_DATA_PATTERN)
    if not existing:
        return 2   # v1 was the manual run before this script existed
    nums = []
    for f in existing:
        m = re.search(r"v(\d+)_data\.json", f)
        if m:
            nums.append(int(m.group(1)))
    return max(nums, default=1) + 1


def _load_previous_data() -> dict | None:
    """Load the most recent data JSON for comparison."""
    existing = sorted(glob.glob(_DATA_PATTERN))
    if not existing:
        return None
    with open(existing[-1], encoding="utf-8") as f:
        return json.load(f)

# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkResult:
    classifier: str
    test_name: str
    expected_category: str
    expected_tag: str
    category: str = "ERROR"
    tag: str = "ERROR"
    summary: str = ""
    latency_ms: float = 0.0
    error: str = ""

    @property
    def category_ok(self) -> bool:
        return self.category == self.expected_category and not self.error

    @property
    def tag_ok(self) -> bool:
        return self.tag == self.expected_tag and not self.error


async def run_single(classifier, text: str, preprocessor: TextPreprocessor):
    processed = preprocessor.process(text)
    t0 = time.perf_counter()
    try:
        result = await classifier.classify(processed)
        elapsed = (time.perf_counter() - t0) * 1000
        return result, elapsed, ""
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        return None, elapsed, str(e)


async def run_benchmark() -> list[BenchmarkResult]:
    preprocessor = TextPreprocessor()
    print("Inicializando classificadores...")
    classifiers = [
        ("ClassicNLP",   ClassicNLPClassifier()),
        ("HuggingFace",  HuggingFaceClassifier()),
        ("Claude",       ClaudeClassifier()),
    ]

    results: list[BenchmarkResult] = []
    for tc in TEST_CASES:
        print(f"\n--- {tc.name} ---")
        for clf_name, clf in classifiers:
            print(f"  [{clf_name}]...", end="", flush=True)
            result, latency, error = await run_single(clf, tc.text, preprocessor)
            br = BenchmarkResult(
                classifier=clf_name,
                test_name=tc.name,
                expected_category=tc.expected_category,
                expected_tag=tc.expected_tag,
                latency_ms=latency,
                error=error,
            )
            if result:
                br.category = result.category
                br.tag = result.tag
                br.summary = (result.summary or "")[:100]
            status = "ERROR" if error else f"{br.category}/{br.tag}"
            print(f" {status} ({latency:.0f}ms)")
            results.append(br)
    return results

# ---------------------------------------------------------------------------
# Accuracy helpers
# ---------------------------------------------------------------------------

def _accuracy(results: list[BenchmarkResult], clf_name: str, field: str) -> tuple[int, int]:
    rows = [r for r in results if r.classifier == clf_name and not r.error]
    correct = sum(1 for r in rows if getattr(r, f"{field}_ok"))
    return correct, len(rows)

# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    results: list[BenchmarkResult],
    version: int,
    note: str,
    prev_data: dict | None,
) -> str:
    clf_names = ["ClassicNLP", "HuggingFace", "Claude"]
    today = date.today().isoformat()
    lines = []

    lines.append(f"# Benchmark Comparativo — Classificadores de Email — v{version}")
    lines.append(f"\n**Versão:** v{version}  \n**Data:** {today}  \n**Casos de teste:** {len(TEST_CASES)}  ")
    lines.append(f"**Modelos:** ClassicNLP (TF-IDF + LR), HuggingFace (mDeBERTa-v3 zero-shot), Claude (claude-sonnet-4-20250514)  ")
    if note:
        lines.append(f"**Nota:** {note}\n")

    # -----------------------------------------------------------------------
    # Delta vs previous version
    # -----------------------------------------------------------------------
    if prev_data:
        prev_ver = prev_data.get("version", version - 1)
        lines.append(f"\n## Delta vs v{prev_ver}\n")
        lines.append("| Modelo | Acurácia (cat) v{pv} | Acurácia (cat) v{cv} | Δ |".format(pv=prev_ver, cv=version))
        lines.append("|--------|----------------------|----------------------|---|")
        for clf in clf_names:
            prev_acc = prev_data.get("accuracy", {}).get(clf, {})
            p_c, p_t = prev_acc.get("cat_correct", 0), prev_acc.get("cat_total", 1)
            c, t = _accuracy(results, clf, "category")
            prev_pct = p_c / p_t * 100 if p_t else 0
            curr_pct = c / t * 100 if t else 0
            delta = curr_pct - prev_pct
            sign = "+" if delta >= 0 else ""
            lines.append(f"| {clf} | {p_c}/{p_t} ({prev_pct:.0f}%) | {c}/{t} ({curr_pct:.0f}%) | {sign}{delta:.0f}pp |")
        lines.append("")

    # -----------------------------------------------------------------------
    # Scorecard
    # -----------------------------------------------------------------------
    lines.append("\n## Scorecard\n")
    lines.append("| Caso de Teste | Esperado (cat/tag) | ClassicNLP | HuggingFace | Claude |")
    lines.append("|---|---|:---:|:---:|:---:|")
    test_names = list(dict.fromkeys(r.test_name for r in results))
    for tn in test_names:
        row_results = {r.classifier: r for r in results if r.test_name == tn}
        first = next(iter(row_results.values()))
        expected = f"{first.expected_category} / {first.expected_tag}"
        cells = []
        for clf in clf_names:
            r = row_results.get(clf)
            if not r or r.error:
                cells.append("ERR")
            elif r.category_ok and r.tag_ok:
                cells.append("✓✓")
            elif r.category_ok:
                cells.append("✓~")
            else:
                cells.append("✗")
        lines.append(f"| {tn} | `{expected}` | {cells[0]} | {cells[1]} | {cells[2]} |")

    lines.append("\n> ✓✓ category + tag corretos · ✓~ category certa, tag errada · ✗ category errada\n")

    lines.append("\n## Acurácia Consolidada\n")
    lines.append("| Modelo | Category (n/total) | % | Tag (n/total) | % |")
    lines.append("|--------|-------------------|---|--------------|---|")
    for clf in clf_names:
        c_c, c_t = _accuracy(results, clf, "category")
        t_c, t_t = _accuracy(results, clf, "tag")
        c_pct = c_c / c_t * 100 if c_t else 0
        t_pct = t_c / t_t * 100 if t_t else 0
        lines.append(f"| {clf} | {c_c}/{c_t} | {c_pct:.0f}% | {t_c}/{t_t} | {t_pct:.0f}% |")

    # -----------------------------------------------------------------------
    # Results per test case
    # -----------------------------------------------------------------------
    lines.append("\n## Resultados por Caso de Teste\n")
    for tn in test_names:
        tc_results = {r.classifier: r for r in results if r.test_name == tn}
        first = next(iter(tc_results.values()))
        lines.append(f"### {tn}")
        lines.append(f"**Esperado:** `{first.expected_category} / {first.expected_tag}`\n")
        lines.append("| Modelo | Categoria | Tag | Latência | Resumo |")
        lines.append("|--------|-----------|-----|----------|--------|")
        for clf in clf_names:
            r = tc_results.get(clf)
            if not r:
                continue
            if r.error:
                lines.append(f"| {clf} | ERRO | — | {r.latency_ms:.0f}ms | `{r.error[:60]}` |")
            else:
                cat_icon = "✓" if r.category_ok else "✗"
                tag_icon = "✓" if r.tag_ok else "~"
                lines.append(f"| {clf} | {cat_icon} **{r.category}** | {tag_icon} {r.tag} | {r.latency_ms:.0f}ms | {r.summary[:80]} |")
        lines.append("")

    # -----------------------------------------------------------------------
    # Latency
    # -----------------------------------------------------------------------
    lines.append("\n## Latência por Modelo\n")
    lines.append("| Modelo | Média (ms) | Mín (ms) | Máx (ms) |")
    lines.append("|--------|-----------|---------|---------|")
    for clf in clf_names:
        clf_results = [r for r in results if r.classifier == clf and not r.error]
        if clf_results:
            lats = [r.latency_ms for r in clf_results]
            lines.append(f"| {clf} | {sum(lats)/len(lats):.0f} | {min(lats):.0f} | {max(lats):.0f} |")

    # -----------------------------------------------------------------------
    # Concordância
    # -----------------------------------------------------------------------
    lines.append("\n## Concordância entre Modelos\n")
    lines.append("| Par | Concordância (category) |")
    lines.append("|-----|------------------------|")
    for a, b in [("ClassicNLP", "HuggingFace"), ("ClassicNLP", "Claude"), ("HuggingFace", "Claude")]:
        common = set(r.test_name for r in results if r.classifier == a and not r.error) & \
                 set(r.test_name for r in results if r.classifier == b and not r.error)
        if not common:
            continue
        agree = sum(
            1 for tn in common
            if next((r.category for r in results if r.classifier == a and r.test_name == tn), None) ==
               next((r.category for r in results if r.classifier == b and r.test_name == tn), None)
        )
        lines.append(f"| {a} vs {b} | {agree}/{len(common)} ({agree/len(common)*100:.0f}%) |")

    # -----------------------------------------------------------------------
    # Qualitative
    # -----------------------------------------------------------------------
    lines.append("""
## Análise Qualitativa

### ClassicNLP (TF-IDF + Logistic Regression)
**Técnicas NLP aplicadas:**
Detecção de idioma (langdetect) → lowercasing → tokenização por regex → remoção de stopwords (NLTK multilíngue) → stemming (SnowballStemmer) → TF-IDF unigramas+bigramas (1500 features) → features manuais (comprimento, `?`, action words) → Logistic Regression → thresholds separados (cat ≥ 0.55, tag ≥ 0.30) → category derivada da tag quando confiante → sumarização extrativa por score TF-IDF

**Pontos fortes:** Latência sub-milissegundo · offline · determinístico · sumarização extrativa funcional
**Limitações:** Sem semântica contextual · não reconhece urgência sem a palavra "urgente" · falha em inglês

---

### HuggingFace (mDeBERTa-v3-base-mnli-xnli, zero-shot)
**Técnicas NLP aplicadas:**
Transformer DeBERTa-v3 (278M parâmetros, multilíngue) → cabeça NLI → hipótese "Este email é sobre {label}" → ranking por probabilidade de entailment → threshold de confiança 0.4

**Pontos fortes:** Zero-shot sem treino · multilíngue · robusto a variações de escrita
**Limitações:** Confunde urgência de marketing com urgência real · labels curtos causam falsos positivos · resumo via primeira sentença (sem semântica)

---

### Claude (claude-sonnet-4-20250514)
**Técnicas NLP aplicadas:**
Prompt engineering com definições + 4 exemplos few-shot + formato JSON estruturado → geração de `category`, `tag`, `summary` e `suggested_response` contextualizados → validação de consistência tag↔category com mapeamento determinístico no post-processing

**Pontos fortes:** Melhor precisão semântica · resumos e respostas personalizados · único que acerta inglês e phishing · distingue "menciona reunião" de "convite de reunião"
**Limitações:** Maior latência · custo por chamada · dependência de API externa

---

## Recomendação de Uso

| Cenário | Modelo |
|---------|--------|
| Precisão máxima + respostas personalizadas | Claude |
| Multilíngue sem custo de API | HuggingFace |
| Offline / latência crítica | ClassicNLP |
| Volume alto (produção) | ClassicNLP triagem + Claude para casos ambíguos |
""")

    # -----------------------------------------------------------------------
    # Histórico de versões
    # -----------------------------------------------------------------------
    lines.append("\n## Histórico de Versões\n")
    lines.append("| Versão | Data | ClassicNLP (cat%) | HuggingFace (cat%) | Claude (cat%) | Nota |")
    lines.append("|--------|------|:-----------------:|:------------------:|:-------------:|------|")

    # Linha v1 hardcoded (executado antes deste script existir)
    lines.append("| v1 | 2026-03-23 | 33% | 58% | 83% | Baseline — dataset original (56 ex), threshold único 0.6 |")

    # Versões intermediárias salvas em JSON
    existing_data = sorted(glob.glob(_DATA_PATTERN))
    shown_versions = {1}
    for f in existing_data:
        m = re.search(r"v(\d+)_data\.json", f)
        if not m:
            continue
        v = int(m.group(1))
        if v in shown_versions or v == version:
            continue
        shown_versions.add(v)
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        acc = d.get("accuracy", {})
        def pct(clf):
            a = acc.get(clf, {})
            c, t = a.get("cat_correct", 0), a.get("cat_total", 1)
            return f"{c/t*100:.0f}%" if t else "—"
        n = d.get("note", "—")
        lines.append(f"| v{v} | {d.get('date','?')} | {pct('ClassicNLP')} | {pct('HuggingFace')} | {pct('Claude')} | {n} |")

    # Versão atual
    c_c, c_t = _accuracy(results, "ClassicNLP", "category")
    h_c, h_t = _accuracy(results, "HuggingFace", "category")
    cl_c, cl_t = _accuracy(results, "Claude", "category")
    c_pct = f"{c_c/c_t*100:.0f}%" if c_t else "—"
    h_pct = f"{h_c/h_t*100:.0f}%" if h_t else "—"
    cl_pct = f"{cl_c/cl_t*100:.0f}%" if cl_t else "—"
    lines.append(f"| **v{version}** | {today} | **{c_pct}** | **{h_pct}** | **{cl_pct}** | {note or '—'} |")

    return "\n".join(lines)


def _build_data_json(results: list[BenchmarkResult], version: int, note: str) -> dict:
    """Serializable summary for diff in future versions."""
    clf_names = ["ClassicNLP", "HuggingFace", "Claude"]
    accuracy = {}
    for clf in clf_names:
        c_c, c_t = _accuracy(results, clf, "category")
        t_c, t_t = _accuracy(results, clf, "tag")
        accuracy[clf] = {"cat_correct": c_c, "cat_total": c_t, "tag_correct": t_c, "tag_total": t_t}

    rows = []
    for r in results:
        rows.append({
            "classifier": r.classifier, "test_name": r.test_name,
            "expected_category": r.expected_category, "expected_tag": r.expected_tag,
            "category": r.category, "tag": r.tag,
            "category_ok": r.category_ok, "tag_ok": r.tag_ok,
            "latency_ms": round(r.latency_ms, 1), "error": r.error,
        })
    return {
        "version": version,
        "date": date.today().isoformat(),
        "note": note,
        "accuracy": accuracy,
        "results": rows,
    }

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--note", default="", help="Descrição das mudanças nesta versão")
    args = parser.parse_args()

    version = _next_version()
    prev_data = _load_previous_data()

    print("=" * 60)
    print(f"BENCHMARK v{version} — Email Classifier (3 modelos)")
    print("=" * 60)

    results = await run_benchmark()

    os.makedirs(_BENCHMARKS_DIR, exist_ok=True)

    # Save data JSON for future diffs
    data = _build_data_json(results, version, args.note)
    data_path = os.path.join(_BENCHMARKS_DIR, f"v{version}_data.json")
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Save versioned markdown
    report = generate_report(results, version, args.note, prev_data)
    md_path = os.path.join(_BENCHMARKS_DIR, f"v{version}_{date.today().isoformat()}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report)

    # Update BENCHMARK.md at repo root (always latest)
    with open(_LATEST_MD, "w", encoding="utf-8") as f:
        f.write(f"<!-- Auto-generated — latest is v{version}. See benchmarks/ for all versions. -->\n\n")
        f.write(report)

    print(f"\nRelatório salvo em: {md_path}")
    print(f"BENCHMARK.md atualizado (v{version})")
    print(f"\nAcurácia (category):")
    for clf in ["ClassicNLP", "HuggingFace", "Claude"]:
        c, t = _accuracy(results, clf, "category")
        lat = [r.latency_ms for r in results if r.classifier == clf and not r.error]
        avg_lat = sum(lat)/len(lat) if lat else 0
        print(f"  {clf}: {c}/{t} ({c/t*100:.0f}%) — {avg_lat:.0f}ms média")


if __name__ == "__main__":
    asyncio.run(main())
