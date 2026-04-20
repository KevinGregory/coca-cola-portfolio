# renderer.py
# Generates the HTML portfolio site and PDF exports.
# All result dicts are plain Python dicts (serialized in analyzer.py)
# so Jinja2 can access every field with dot notation in templates.

from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def build_site(all_results: list, templates_dir: Path, output_dir: Path):
    """Generate index.html + one page per campaign."""
    env = Environment(loader=FileSystemLoader(str(templates_dir)))
    site_dir = output_dir / "site"
    site_dir.mkdir(parents=True, exist_ok=True)

    print("\n🌐 Building HTML site...")

    # Index / overview page
    index_html = env.get_template("portfolio.html").render(results=all_results)
    (site_dir / "index.html").write_text(index_html, encoding="utf-8")
    print("  ✅ index.html")

    # One detail page per campaign
    report_tmpl = env.get_template("ad_report.html")
    for result in all_results:
        page_html = report_tmpl.render(
            campaign=result["campaign"],
            audience=result["audience"],
            section_analysis=result["section_analysis"],
            improvements=result["improvements"],
            summary=result["summary"],
            tiers=result.get("tiers", {}),
            visual_svg=result["campaign"].get("visual_svg", ""),
            all_results=all_results,
        )
        out_path = site_dir / f"{result['campaign']['id']}.html"
        out_path.write_text(page_html, encoding="utf-8")
        print(f"  ✅ {out_path.name}")

    print(f"  → Site: {site_dir}")


def build_pdfs(all_results: list, site_dir: Path, output_dir: Path):
    """Convert each HTML campaign report to PDF via WeasyPrint."""
    try:
        from weasyprint import HTML
    except ImportError:
        print("\n⚠️  WeasyPrint not installed — skipping PDF export.")
        print("   Run: uv add weasyprint")
        return

    pdf_dir = output_dir / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    print("\n📄 Generating PDFs...")

    for result in all_results:
        cid = result["campaign"]["id"]
        html_file = site_dir / f"{cid}.html"
        pdf_file  = pdf_dir  / f"{cid}.pdf"
        HTML(filename=str(html_file), base_url=str(site_dir)).write_pdf(str(pdf_file))
        print(f"  ✅ {cid}.pdf")

    print(f"  → PDFs: {pdf_dir}")
