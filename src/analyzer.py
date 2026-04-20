# analyzer.py
# Calls BAML AI functions for each campaign and saves markdown reports.
# Results are returned as plain dicts (not BAML objects) so Jinja2
# templates can access all fields without any special handling.

import os
import json
from pathlib import Path

from baml_client import b


# ── Serializers: BAML object → plain dict ──────────────────────────
# BAML returns Pydantic models. We convert them to plain dicts here
# so Jinja2 templates, JSON saving, and the renderer all work cleanly.

def _audience_to_dict(obj) -> dict:
    return {
        "primary_demographic": obj.primary_demographic,
        "psychographics": list(obj.psychographics),
        "cultural_moment": obj.cultural_moment,
        "emotional_drivers": list(obj.emotional_drivers),
        "geographic_focus": obj.geographic_focus,
        "media_channels": list(obj.media_channels),
    }

def _section_to_dict(obj) -> dict:
    return {
        "section_name": obj.section_name,
        "current_execution": obj.current_execution,
        "strengths": list(obj.strengths),
        "weaknesses": list(obj.weaknesses),
        "improvement": obj.improvement,
        "reasoning": obj.reasoning,
    }

def _section_analysis_to_dict(obj) -> dict:
    return {
        "sections": [_section_to_dict(s) for s in obj.sections],
        "overall_tone": obj.overall_tone,
        "brand_alignment_score": obj.brand_alignment_score,
        "brand_alignment_notes": obj.brand_alignment_notes,
    }

def _improvements_to_dict(obj) -> dict:
    return {
        "headline_rewrite": obj.headline_rewrite,
        "visual_direction": obj.visual_direction,
        "cta_rewrite": obj.cta_rewrite,
        "tone_adjustment": obj.tone_adjustment,
        "modern_relevance": obj.modern_relevance,
        "audience_expansion": obj.audience_expansion,
        "platform_adaptations": list(obj.platform_adaptations),
    }

def _summary_to_dict(obj) -> dict:
    return {
        "strategic_insight": obj.strategic_insight,
        "why_it_worked": obj.why_it_worked,
        "cultural_legacy": obj.cultural_legacy,
        "portfolio_talking_points": list(obj.portfolio_talking_points),
        "skills_demonstrated": list(obj.skills_demonstrated),
    }

def _tier_to_dict(obj) -> dict:
    if obj is None:
        return {}
    return {
        "tier_name": obj.tier_name,
        "tagline": obj.tagline,
        "headline": obj.headline,
        "concept": obj.concept,
        "visual_direction": obj.visual_direction,
        "media_strategy": obj.media_strategy,
        "target_shift": obj.target_shift,
        "risk_level": obj.risk_level,
        "why_it_works": obj.why_it_works,
    }

def _visual_prompt_to_dict(obj) -> dict:
    if obj is None:
        return {}
    return {
        "image_prompt": obj.image_prompt,
        "color_palette": list(obj.color_palette),
        "mood_words": list(obj.mood_words),
        "composition": obj.composition,
    }


# ── Core analysis ───────────────────────────────────────────────────

def analyze_campaign(campaign: dict) -> dict:
    """Run all 4 BAML analyses on a single campaign. Returns plain dicts."""
    print(f"\n🔍 Analyzing: {campaign['name']} ({campaign['year']})")

    print("  → Researching audience...")
    audience_obj = b.ResearchAudience(
        campaign_name=campaign["name"],
        agency=campaign["agency"],
        year=campaign["year"],
        brief=campaign["brief"],
    )
    audience = _audience_to_dict(audience_obj)

    print("  → Analyzing ad sections...")
    section_obj = b.AnalyzeAdSections(
        campaign_name=campaign["name"],
        year=campaign["year"],
        ad_description=campaign["ad_description"],
    )
    section_analysis = _section_analysis_to_dict(section_obj)

    weaknesses_summary = "; ".join([
        f"{s['section_name']}: {'; '.join(s['weaknesses'])}"
        for s in section_analysis["sections"]
        if s["weaknesses"]
    ])

    print("  → Generating improvements...")
    improvements_obj = b.GenerateImprovements(
        campaign_name=campaign["name"],
        year=campaign["year"],
        audience=audience["primary_demographic"],
        current_weaknesses=weaknesses_summary,
    )
    improvements = _improvements_to_dict(improvements_obj)

    analysis_summary = (
        f"Brand alignment score: {section_analysis['brand_alignment_score']}/10. "
        f"Overall tone: {section_analysis['overall_tone']}. "
        f"Key weaknesses: {weaknesses_summary[:300]}"
    )

    print("  → Generating portfolio summary...")
    summary_obj = b.SummarizeCampaign(
        campaign_name=campaign["name"],
        agency=campaign["agency"],
        year=campaign["year"],
        brief=campaign["brief"],
        analysis_summary=analysis_summary,
    )
    summary = _summary_to_dict(summary_obj)

    print(f"  ✅ Done: {campaign['name']}")

    return {
        "campaign": campaign,
        "audience": audience,
        "section_analysis": section_analysis,
        "improvements": improvements,
        "summary": summary,
        "tiers": {},           # populated by orchestrator if --tiers flag used
        "visual_prompts": {},  # populated by orchestrator if --tiers flag used
    }


def save_markdown_report(result: dict, output_dir: Path):
    """Save a campaign analysis as a Markdown report."""
    campaign  = result["campaign"]
    audience  = result["audience"]
    sections  = result["section_analysis"]
    improvements = result["improvements"]
    summary   = result["summary"]

    lines = [
        f"# {campaign['name']} ({campaign['year']})",
        f"**Agency:** {campaign['agency']}  ",
        f"**Year:** {campaign['year']}",
        "",
        "---",
        "",
        "## Campaign Brief",
        campaign["brief"],
        "",
        "---",
        "",
        "## Audience Research",
        f"**Primary Demographic:** {audience['primary_demographic']}",
        f"**Geographic Focus:** {audience['geographic_focus']}",
        f"**Cultural Moment:** {audience['cultural_moment']}",
        "",
        "**Psychographics:**",
        *[f"- {p}" for p in audience["psychographics"]],
        "",
        "**Emotional Drivers:**",
        *[f"- {e}" for e in audience["emotional_drivers"]],
        "",
        "**Media Channels:**",
        *[f"- {m}" for m in audience["media_channels"]],
        "",
        "---",
        "",
        "## Ad Section Analysis",
        f"**Overall Tone:** {sections['overall_tone']}  ",
        f"**Brand Alignment Score:** {sections['brand_alignment_score']}/10  ",
        f"**Notes:** {sections['brand_alignment_notes']}",
        "",
    ]

    for s in sections["sections"]:
        lines += [
            f"### {s['section_name']}",
            f"**Current:** {s['current_execution']}",
            "",
            "**Strengths:**",
            *[f"- {x}" for x in s["strengths"]],
            "",
            "**Weaknesses:**",
            *[f"- {x}" for x in s["weaknesses"]],
            "",
            f"**Improvement:** {s['improvement']}",
            f"**Reasoning:** {s['reasoning']}",
            "",
        ]

    lines += [
        "---",
        "",
        "## Recommended Improvements",
        f"**Headline Rewrite:** {improvements['headline_rewrite']}",
        f"**Visual Direction:** {improvements['visual_direction']}",
        f"**CTA Rewrite:** {improvements['cta_rewrite']}",
        f"**Tone Adjustment:** {improvements['tone_adjustment']}",
        f"**Modern Relevance:** {improvements['modern_relevance']}",
        f"**Audience Expansion:** {improvements['audience_expansion']}",
        "",
        "**Platform Adaptations:**",
        *[f"- {p}" for p in improvements["platform_adaptations"]],
        "",
        "---",
        "",
        "## Portfolio Summary",
        f"**Strategic Insight:** {summary['strategic_insight']}",
        f"**Why It Worked:** {summary['why_it_worked']}",
        f"**Cultural Legacy:** {summary['cultural_legacy']}",
        "",
        "**Portfolio Talking Points:**",
        *[f"- {t}" for t in summary["portfolio_talking_points"]],
        "",
        "**Skills Demonstrated:**",
        *[f"- {s}" for s in summary["skills_demonstrated"]],
    ]

    # Append tiers if they were generated
    tiers = result.get("tiers", {})
    if tiers:
        lines += ["", "---", "", "## Campaign Tiers (Conservative / Balanced / Bold)"]
        for tier_name, tier in tiers.items():
            if tier:
                lines += [
                    f"### {tier.get('tier_name', tier_name.capitalize())} — {tier.get('risk_level', '')} Risk",
                    f"**Tagline:** {tier.get('tagline', '')}",
                    f"**Headline:** {tier.get('headline', '')}",
                    f"**Concept:** {tier.get('concept', '')}",
                    f"**Why it works:** {tier.get('why_it_works', '')}",
                    "",
                ]

    filename = output_dir / f"{campaign['id']}.md"
    filename.write_text("\n".join(lines), encoding="utf-8")
    print(f"  💾 Saved: {filename.name}")


def run_all_analyses(campaigns: list, output_dir: Path) -> list:
    """Analyze all campaigns and return a list of result dicts."""
    all_results = []
    for campaign in campaigns:
        result = analyze_campaign(campaign)
        save_markdown_report(result, output_dir)
        all_results.append(result)
    return all_results
