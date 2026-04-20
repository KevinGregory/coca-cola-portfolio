# cli.py
# Typer CLI entry point — borrowed pattern from Alfred (github.com/KevinGregory/alfred).
# After `uv sync`, run: uv run portfolio [OPTIONS] [CAMPAIGN_ID]
#
# Full pipeline order:
#   1. (optional) Live web research per campaign
#   2. Generate stub/real SVG visuals per campaign
#   3. Run core BAML analyses (audience, sections, improvements, summary)
#   4. (optional) Generate Conservative/Balanced/Bold tiers in parallel
#   5. Build HTML portfolio site + PDF exports

import os
import sys
import webbrowser
from pathlib import Path

try:
    import typer
except ImportError:
    print("Typer not installed. Run: uv add typer")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()  # reads .env file automatically — Alfred's secrets pattern
except ImportError:
    pass  # python-dotenv optional; user can export manually

app = typer.Typer(
    name="portfolio",
    help="Coca-Cola Ad Analysis Portfolio — powered by BAML + Claude AI",
    add_completion=False,
)


@app.command()
def run(
    campaign_filter: str = typer.Argument(
        "all",
        help=(
            'Campaign ID to run, or "all". '
            "IDs: buy_the_world, share_a_coke, holidays_coming, open_happiness, real_magic"
        ),
    ),
    backend: str = typer.Option(
        "stub",
        "--backend",
        help="Image backend: stub (SVG, no key needed) | openai (gpt-image-1, needs OPENAI_API_KEY)",
    ),
    research: bool = typer.Option(
        False,
        "--research/--no-research",
        help="Run live Claude web_search per campaign before analysis",
    ),
    tiers: bool = typer.Option(
        False,
        "--tiers/--no-tiers",
        help="Generate Conservative / Balanced / Bold improvement tiers per campaign",
    ),
    no_open: bool = typer.Option(
        False,
        "--no-open",
        help="Don't auto-open the browser after generation",
    ),
    out: Path = typer.Option(
        Path("output"),
        "-o", "--out",
        help="Output directory  [default: output/]",
    ),
):
    """
    Generate the Coca-Cola Ad Analysis Portfolio.

    \b
    Examples:
      uv run portfolio                       # all 5 campaigns, stub SVGs
      uv run portfolio share_a_coke          # one campaign only
      uv run portfolio --research --tiers    # full pipeline with live research
      uv run portfolio --backend openai      # real AI-generated images
      uv run portfolio --no-open             # skip auto-opening browser
    """

    # ── API key check ──────────────────────────────────────────────
    if not os.environ.get("ANTHROPIC_API_KEY"):
        typer.echo(typer.style(
            "\n❌  ANTHROPIC_API_KEY not set.\n"
            "    Copy .env.example → .env and add your key:\n"
            "      cp .env.example .env\n"
            "    Or export manually:\n"
            "      export ANTHROPIC_API_KEY=sk-ant-...\n",
            fg=typer.colors.RED,
        ))
        raise typer.Exit(1)

    # Propagate image backend to image_backends.py via env
    os.environ["COCA_IMAGE_BACKEND"] = backend

    # ── Banner ─────────────────────────────────────────────────────
    typer.echo(typer.style("\n━" * 52, fg=typer.colors.RED))
    typer.echo(typer.style("  Coca-Cola Ad Analysis Portfolio", bold=True))
    typer.echo(typer.style("━" * 52, fg=typer.colors.RED))
    typer.echo(f"\n  Filter  : {campaign_filter}")
    typer.echo(f"  Backend : {backend}")
    typer.echo(f"  Research: {'yes (live web search)' if research else 'no'}")
    typer.echo(f"  Tiers   : {'yes (Conservative / Balanced / Bold)' if tiers else 'no'}")
    typer.echo(f"  Output  : {out}\n")

    # ── Lazy imports (keeps CLI startup fast — Alfred pattern) ──────
    src_dir = Path(__file__).parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    from campaigns import CAMPAIGNS
    from analyzer import run_all_analyses
    from renderer import build_site, build_pdfs
    from image_backends import generate_campaign_visual
    from research import research_campaign
    from orchestrator import run_tiers_in_parallel

    # ── Filter campaigns ───────────────────────────────────────────
    if campaign_filter != "all":
        campaigns_to_run = [c for c in CAMPAIGNS if c["id"] == campaign_filter]
        if not campaigns_to_run:
            valid = ", ".join(c["id"] for c in CAMPAIGNS)
            typer.echo(typer.style(
                f"❌  Unknown campaign: '{campaign_filter}'\n"
                f"    Valid IDs: {valid}",
                fg=typer.colors.RED,
            ))
            raise typer.Exit(1)
    else:
        campaigns_to_run = list(CAMPAIGNS)

    # ── Phase 1: Live web research ──────────────────────────────────
    if research:
        typer.echo(typer.style("  [1/4] Live web research...", fg=typer.colors.YELLOW))
        campaigns_to_run = [research_campaign(c) for c in campaigns_to_run]
    else:
        typer.echo("  [1/4] Skipping research  (--research to enable)")

    # ── Phase 2: Stub / real visuals ───────────────────────────────
    typer.echo(typer.style(f"\n  [2/4] Generating visuals ({backend})...", fg=typer.colors.YELLOW))
    for campaign in campaigns_to_run:
        campaign["visual_svg"] = generate_campaign_visual(campaign)
        typer.echo(f"     ✅ {campaign['id']}")

    # ── Phase 3: Core BAML analyses ────────────────────────────────
    typer.echo(typer.style("\n  [3/4] Running AI analyses via BAML...", fg=typer.colors.YELLOW))
    out.mkdir(parents=True, exist_ok=True)
    reports_dir = out / "reports"
    reports_dir.mkdir(exist_ok=True)
    all_results = run_all_analyses(campaigns_to_run, reports_dir)

    # ── Phase 4: Three-tier parallel generation ─────────────────────
    if tiers:
        typer.echo(typer.style(
            "\n  [4/4] Generating tiers in parallel (Conservative / Balanced / Bold)...",
            fg=typer.colors.YELLOW,
        ))
        for result in all_results:
            # audience is now a plain dict — use ['key'] not .attribute
            audience_str = result["audience"]["primary_demographic"]
            result["tiers"] = run_tiers_in_parallel(result["campaign"], audience_str)
    else:
        typer.echo("  [4/4] Skipping tiers       (--tiers to enable)")

    # ── Phase 5: HTML site + PDFs ──────────────────────────────────
    typer.echo(typer.style("\n  [5/5] Building portfolio site + PDFs...", fg=typer.colors.YELLOW))
    templates_dir = src_dir / "templates"
    build_site(all_results, templates_dir, out)
    build_pdfs(all_results, out / "site", out)

    # ── Done ───────────────────────────────────────────────────────
    index_path = (out / "site" / "index.html").resolve()
    typer.echo(typer.style("\n━" * 52, fg=typer.colors.RED))
    typer.echo(typer.style("  ✅  Complete!", bold=True, fg=typer.colors.GREEN))
    typer.echo(typer.style("━" * 52, fg=typer.colors.RED))
    typer.echo(f"\n  📁  Reports  →  {reports_dir}")
    typer.echo(f"  🌐  Site     →  {index_path}")
    typer.echo(f"  📄  PDFs     →  {out / 'pdfs'}\n")

    if not no_open:
        try:
            webbrowser.open(f"file://{index_path}")
        except Exception:
            typer.echo(f"  Open manually: file://{index_path}")


def main():
    """Registered as 'portfolio' in pyproject.toml [project.scripts]."""
    src_dir = Path(__file__).parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    app()


if __name__ == "__main__":
    main()
