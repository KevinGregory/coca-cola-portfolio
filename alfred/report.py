from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup


TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def render_report(run_dir: Path, company: str, dossier, personas, campaigns, past_campaigns) -> Path:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "j2"]),
    )
    template = env.get_template("report.html.j2")
    # ad_html is a trusted Claude-produced fragment we want rendered as-is.
    rendered = template.render(
        company=company,
        dossier=dossier,
        personas=personas,
        past_campaigns=past_campaigns,
        campaigns=[
            {
                "brief": c.brief,
                "visual": c.visual_prompt,
                "image_rel": c.image_rel,
                "ad_html": Markup(c.ad_html),
                "tier_name": str(c.brief.tier).split(".")[-1],
            }
            for c in campaigns
        ],
    )
    out_path = run_dir / "report.html"
    out_path.write_text(rendered, encoding="utf-8")
    return out_path
