from __future__ import annotations

import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from alfred import research
from alfred.image_backends import ImageBackend, build_backend
from alfred.report import render_report

# Target size per research chunk in characters — small enough that each Gemini
# call is snappy, large enough to preserve paragraph-level context.
_CHUNK_TARGET_CHARS = 6000
# Below this, skip the summarizer entirely — raw research is already compact.
_SUMMARIZE_THRESHOLD = 4000


def _log(msg: str) -> None:
    print(f"[alfred] {msg}", file=sys.stderr, flush=True)


def _slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "company"


@dataclass
class CampaignOutput:
    brief: object       # baml_client.types.CampaignBrief
    visual_prompt: object  # baml_client.types.VisualPrompt
    image_path: Path    # absolute
    image_rel: str      # path relative to run dir, for use in HTML
    ad_html: str        # self-contained ad-card HTML from RenderAdHTML


def run(company: str, *, out_root: Path | None = None, image_backend: ImageBackend | None = None) -> Path:
    """Run the full pipeline for `company` and return the path to the generated report.html."""
    from baml_client import b
    from baml_client.types import Tier

    out_root = out_root or Path("out")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = out_root / f"{timestamp}-{_slugify(company)}"
    run_dir.mkdir(parents=True, exist_ok=True)

    image_backend = image_backend or build_backend()

    t0 = time.time()
    _log(f"researching {company!r}…")
    research_result = research.investigate(company)
    _log(f"  got {len(research_result.raw_text):,} chars of research, {len(research_result.sources)} sources ({time.time()-t0:.1f}s)")

    condensed = _condense_research(company, research_result.raw_text)

    _log("extracting dossier…")
    dossier = b.ExtractDossier(
        company_name=company,
        raw_research=condensed,
        sources=research_result.sources,
    )

    _log("analyzing past campaigns…")
    past_campaigns = b.AnalyzePastCampaigns(
        company_name=company,
        raw_research=research_result.raw_text,
    )
    _log(f"  found {len(past_campaigns)} past campaigns")

    _log("identifying personas…")
    personas = b.IdentifyPersonas(dossier=dossier)

    # Sequential on purpose: 3 parallel Claude calls can burst past low-tier
    # input-TPM budgets. Running one at a time gives the rolling window room
    # to drain. Swap to ThreadPoolExecutor on Tier 2+.
    _log(f"generating 3 campaigns sequentially (backend={image_backend.__class__.__name__})…")
    campaigns: list[CampaignOutput] = []
    for tier in (Tier.Conservative, Tier.Balanced):
        _log(f"  → {tier.value}")
        brief = b.GenerateCampaign(dossier=dossier, personas=personas, tier=tier)
        campaigns.append(_finalize_campaign(brief, run_dir, image_backend))
    _log("  → Bold (Opus)")
    bold_brief = b.GenerateBoldCampaign(dossier=dossier, personas=personas)
    campaigns.append(_finalize_campaign(bold_brief, run_dir, image_backend))

    _log("assembling report…")
    report_path = render_report(run_dir, company, dossier, personas, campaigns, past_campaigns)
    _log(f"done → {report_path}  ({time.time()-t0:.1f}s total)")
    return report_path


def _chunk_by_paragraph(text: str, target_chars: int = _CHUNK_TARGET_CHARS) -> list[str]:
    """Greedy pack paragraphs into chunks of ~target_chars so semantic units stay intact."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for p in paragraphs:
        # A single paragraph larger than target gets split on sentence boundaries.
        if len(p) > target_chars:
            if current:
                chunks.append("\n\n".join(current))
                current, current_len = [], 0
            sentences = p.replace(". ", ".\n").split("\n")
            buf, buf_len = [], 0
            for s in sentences:
                if buf_len + len(s) + 1 > target_chars and buf:
                    chunks.append(" ".join(buf))
                    buf, buf_len = [s], len(s)
                else:
                    buf.append(s)
                    buf_len += len(s) + 1
            if buf:
                chunks.append(" ".join(buf))
            continue

        if current_len + len(p) + 2 > target_chars and current:
            chunks.append("\n\n".join(current))
            current, current_len = [p], len(p)
        else:
            current.append(p)
            current_len += len(p) + 2

    if current:
        chunks.append("\n\n".join(current))
    return chunks


def _condense_research(company: str, raw_text: str) -> str:
    """Map-reduce via Gemini: chunked bullet-extraction then a final consolidation pass."""
    from baml_client import b

    if len(raw_text) < _SUMMARIZE_THRESHOLD:
        _log(f"  research is {len(raw_text):,} chars — under threshold, skipping summarization")
        return raw_text

    chunks = _chunk_by_paragraph(raw_text)
    _log(f"  map: bulletizing {len(chunks)} chunks via Gemini 2.5 Flash…")

    def summarize(idx: int, chunk: str) -> tuple[int, str]:
        return idx, b.SummarizeResearchChunk(company_name=company, chunk=chunk)

    with ThreadPoolExecutor(max_workers=min(len(chunks), 4)) as pool:
        results = list(pool.map(lambda args: summarize(*args), enumerate(chunks)))

    results.sort(key=lambda r: r[0])
    mapped = "\n".join(s for _, s in results)
    _log(f"    mapped: {len(raw_text):,} → {len(mapped):,} chars")

    _log("  reduce: consolidating into briefing…")
    briefing = b.CondenseToBriefing(company_name=company, mapped_bullets=mapped)

    # Belt-and-braces: even if Gemini ignores the size cap, hard-clip before Claude sees it.
    HARD_CAP = 3000
    if len(briefing) > HARD_CAP:
        briefing = briefing[:HARD_CAP].rsplit("\n", 1)[0] + "\n- …(truncated)"

    _log(f"    briefing: {len(mapped):,} → {len(briefing):,} chars (vs raw {len(raw_text):,})")
    return briefing


def _finalize_campaign(brief, run_dir: Path, backend: ImageBackend) -> CampaignOutput:
    from baml_client import b
    tier_name = str(brief.tier).split(".")[-1].lower()
    visual = b.GenerateVisualPrompt(campaign=brief)
    image_path = backend.generate(visual.prompt, visual.aspect, run_dir / f"{tier_name}")
    image_rel = image_path.name
    mockup = b.RenderAdHTML(campaign=brief, image_src=image_rel)
    return CampaignOutput(
        brief=brief,
        visual_prompt=visual,
        image_path=image_path,
        image_rel=image_rel,
        ad_html=mockup.html,
    )
