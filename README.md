# Alfred

An agentic tool that turns a single input — a company name — into three differentiated ad campaign proposals (Conservative, Balanced, Bold), each with research-grounded strategy, ad copy, and a rendered creative mockup. One self-contained HTML report falls out the other end.

Built with **Python + [BAML](https://docs.boundaryml.com/)** as a portfolio piece for an advertising-agency interview. The point is to show production use of modern agent tooling: web-search tool loops, typed LLM functions, parallel fan-out, and image generation — wired into one clean CLI.

## What it does

```
company name ─► research (Claude + web_search loop)
             ─► structured dossier (BAML: ExtractDossier)
             ─► audience personas (BAML: IdentifyPersonas)
             ─► campaign history (BAML: AnalyzePastCampaigns)
                  • 2–6 past campaigns with concept, channels, outcome, significance
             ─► three campaigns in parallel:
                  • Conservative (Sonnet) — play to existing brand equity
                  • Balanced (Sonnet)     — one fresh mechanic, still on-brand
                  • Bold (Opus)           — stunt-worthy, PR-bait
                for each:
                  ▸ GenerateCampaign      — typed CampaignBrief
                  ▸ GenerateVisualPrompt  — image-gen prompt
                  ▸ image backend         — gpt-image-1 / Flux / stub SVG
                  ▸ RenderAdHTML          — inline-styled ad card
             ─► out/<run>/report.html (tabbed: Brief · Ad History · Personas · per-campaign)
```

## Setup

This project is managed with [**uv**](https://docs.astral.sh/uv/). Install it first if you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# or: brew install uv
```

Then from the repo root:

```bash
# 1. Sync dependencies into a local .venv (reads pyproject.toml + uv.lock).
uv sync

# 2. Generate the BAML client code.
uv run baml-cli generate

# 3. Configure secrets.
cp .env.example .env
# Fill in ANTHROPIC_API_KEY (+ OPENAI_API_KEY if using the default image backend).
```

`uv sync` installs the exact versions pinned in `uv.lock`, so you get the same environment the project was developed against. Python 3.12+ is required; uv will fetch a matching interpreter automatically if you don't have one.

## Run

```bash
uv run alfred "Liquid Death"
# opens out/<timestamp>-liquid-death/report.html in your browser
```

`uv run` executes the command inside the project's venv without needing to activate it. If you'd rather activate it once and drop the prefix, `source .venv/bin/activate` and then call `alfred ...` directly.

Offline / no image API key:

```bash
uv run alfred "Liquid Death" --backend stub
```

Options:

- `--backend openai|replicate|stub` — override `ALFRED_IMAGE_BACKEND`
- `--no-open` — don't auto-open the browser
- `-o, --out` — output directory (default `out/`)

Typical runtime: 2–4 minutes (research is the long tail). Cost: roughly $0.50–$1.00 per run with Claude + gpt-image-1.

## Project layout

```
baml_src/                  Typed BAML functions
  clients.baml             LLM client definitions (Sonnet, SonnetLong, Opus, GeminiFlash)
  dossier.baml             ExtractDossier → CompanyDossier
  campaigns_history.baml   AnalyzePastCampaigns → PastCampaign[]
  personas.baml            IdentifyPersonas → Persona[]
  campaign.baml            GenerateCampaign / GenerateBoldCampaign → CampaignBrief
  summarize.baml           Map-reduce research compression (Gemini)
alfred/                    Python orchestration
  research.py              Anthropic web_search agent loop
  image_backends.py        OpenAI / Replicate / Stub backends
  orchestrator.py          Pipeline: research → dossier → history → personas → campaigns
  report.py                Jinja2 assembly
  cli.py                   Typer entry point
templates/
  report.html.j2           Tabbed single-file HTML report
```

## Why these choices

| Decision | Why |
|---|---|
| BAML over raw SDK calls | Typed outputs + playground testing. Each function is unit-testable in isolation, which is the right primitive for multi-step agent work. |
| Claude `web_search_20250305` over Gemini Deep Research | Claude's tool returns in seconds, not 20 minutes. Faster to iterate during the build. |
| Opus for Bold, Sonnet for the rest | Taste matters most on the risky creative — it's where a better model earns its keep. Sonnet is fine for extraction and on-brand concepts. |
| `gpt-image-1` default, Flux + stub alternatives | `gpt-image-1` is the cheapest path to a decent ad mockup; `stub` lets the full pipeline run with no image API key so the code is demo-able anywhere. |
| `AnalyzePastCampaigns` uses full raw research, not condensed | The map-reduce condensation aggressively truncates to ~3,000 chars. Campaign names, taglines, and dates are exactly the specifics that get lost — so the history function gets the uncompressed text. |
| Tabbed HTML report, still one file | Each section (Brief, Ad History, Personas, and one tab per campaign) is navigable without breaking the single-file share model. Pure JS — no frameworks, no build step. |

## Limits / non-goals

- No persistence or multi-user — this is a desktop CLI, not a service.
- No brand-safety/legal review pass on generated copy. A human still reads before anyone pitches.
- Research tops out at ~8 `web_search` calls per run. It's a pitch-prep briefing, not an investigative report.

---
