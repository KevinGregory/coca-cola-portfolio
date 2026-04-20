# main.py
# Entry point for running without the CLI.
# For full CLI (--research, --tiers, --backend flags): uv run portfolio

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from campaigns import CAMPAIGNS
from analyzer import run_all_analyses
from renderer import build_site, build_pdfs
from image_backends import generate_campaign_visual


def check_api_key():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("❌ ANTHROPIC_API_KEY not set.")
        print("   cp .env.example .env  # then add your key")
        sys.exit(1)
    print(f"✅ API key found ({key[:12]}...)")


def main():
    print("=" * 60)
    print("  Coca-Cola Ad Analysis Portfolio")
    print("  Tip: `uv run portfolio --help` for CLI options")
    print("=" * 60)

    project_root = Path(__file__).parent.parent
    check_api_key()

    output_dir = project_root / "output"
    reports_dir = output_dir / "reports"
    templates_dir = project_root / "src" / "templates"

    for d in [reports_dir, output_dir / "site", output_dir / "pdfs"]:
        d.mkdir(parents=True, exist_ok=True)

    # Generate stub visuals for each campaign (Alfred image backend pattern)
    print("\n🎨 Generating campaign visuals...")
    for campaign in CAMPAIGNS:
        campaign["visual_svg"] = generate_campaign_visual(campaign)

    # Run BAML analyses
    print("\n🔍 Running AI analyses via BAML...")
    all_results = run_all_analyses(CAMPAIGNS, reports_dir)

    # Build HTML + PDFs
    print("\n🌐 Building HTML site...")
    build_site(all_results, templates_dir, output_dir)
    print("\n📄 Exporting PDFs...")
    build_pdfs(all_results, output_dir / "site", output_dir)

    print(f"\n✅ Complete! Open: {(output_dir / 'site' / 'index.html').resolve()}\n")


if __name__ == "__main__":
    main()
