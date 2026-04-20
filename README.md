# Coca-Cola Ad Analysis Portfolio

A portfolio project that uses **Claude AI** (via BAML) to analyze iconic Coca-Cola campaigns.
Heavily inspired by **[Alfred](https://github.com/KevinGregory/alfred)** — same stack, same domain,
several patterns borrowed and adapted directly.

Built with: **Python · BAML · UV · Jinja2 · WeasyPrint · Typer**

---

## What Alfred contributed to this project

| Alfred pattern | How we use it |
|---|---|
| Web search agent loop (`research.py`) | Live campaign research via `claude web_search_20250305` |
| Three campaign tiers in parallel | Conservative / Balanced / Bold improvement directions |
| Opus for Bold, Sonnet for the rest | Tiered model routing in `campaign_tiers.baml` |
| Image backends: stub / openai | SVG mockups by default, real images with `--backend openai` |
| Typer CLI entry point | `uv run portfolio` with `--research`, `--tiers`, `--backend` flags |
| `.env` file for secrets | `cp .env.example .env` instead of manual `export` |
| Self-contained HTML report | Single-file output option |
| `concurrent.futures` parallel fan-out | All three tiers run simultaneously — ~60% faster |

---

## Setup

### 1. Install UV
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install BAML CLI
```bash
uv tool install baml-cli
```

### 3. Install dependencies
```bash
cd coca-cola-portfolio
uv sync
```

### 4. Generate BAML client
```bash
baml-cli generate
```

### 5. Configure secrets (Alfred's pattern)
```bash
cp .env.example .env
# Open .env and add your ANTHROPIC_API_KEY
```

---

## Usage

### Basic run (all 5 campaigns, stub SVG images)
```bash
uv run portfolio
```

### One campaign only
```bash
uv run portfolio share_a_coke
```

### Full pipeline — live research + three improvement tiers
```bash
uv run portfolio --research --tiers
```

### Real AI-generated images (requires OPENAI_API_KEY in .env)
```bash
uv run portfolio --backend openai
```

### All options
```bash
uv run portfolio --help
```

```
Arguments:
  campaign_filter    Campaign ID or "all" [default: all]
                     IDs: buy_the_world, share_a_coke, holidays_coming,
                          open_happiness, real_magic

Options:
  --backend          stub|openai  [default: stub]
  --research         Run live web search per campaign
  --tiers            Generate Conservative/Balanced/Bold improvement tiers
  --no-open          Don't auto-open browser
  -o, --out          Output directory  [default: output/]
```

Typical runtime: 2–4 min with `--research --tiers`. Cost: ~$0.50–$1.00 per full run.

---

## Project structure

```
coca-cola-portfolio/
├── .env.example                # Secrets template (Alfred pattern)
├── pyproject.toml              # UV project config + CLI entry point
├── baml_src/
│   ├── clients.baml            # AI model config
│   ├── ad_analysis.baml        # Core analysis functions
│   └── campaign_tiers.baml     # Conservative/Balanced/Bold (Alfred pattern)
├── baml_client/                # Auto-generated — don't edit
├── src/
│   ├── cli.py                  # Typer CLI (Alfred pattern)
│   ├── main.py                 # Direct entry point (no CLI)
│   ├── campaigns.py            # Campaign data
│   ├── analyzer.py             # BAML analysis + markdown export
│   ├── orchestrator.py         # Parallel fan-out (Alfred pattern)
│   ├── research.py             # Web search agent loop (Alfred pattern)
│   ├── image_backends.py       # Stub SVG / OpenAI (Alfred pattern)
│   ├── renderer.py             # HTML + PDF generation
│   └── templates/
│       ├── portfolio.html      # Index page
│       └── ad_report.html      # Campaign detail page
└── output/
    ├── reports/                # Markdown
    ├── site/                   # HTML portfolio
    └── pdfs/                   # PDF exports
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'baml_client'`**
→ Run `baml-cli generate`

**API key error**
→ `cp .env.example .env` then add your key

**WeasyPrint on macOS**
→ `brew install pango libffi`

**WeasyPrint on Linux**
→ `sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0`
