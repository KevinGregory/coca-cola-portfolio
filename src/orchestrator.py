# orchestrator.py
# Alfred-style parallel fan-out for three campaign tiers.
# All BAML objects are serialized to plain dicts here so the
# rest of the pipeline (renderer, Jinja2) can consume them cleanly.

import concurrent.futures
from baml_client import b


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


def _run_conservative(campaign: dict, audience: str) -> tuple:
    obj = b.GenerateConservativeTier(
        campaign_name=campaign["name"], year=campaign["year"],
        agency=campaign["agency"], brief=campaign["brief"],
        original_audience=audience,
    )
    return "conservative", _tier_to_dict(obj)


def _run_balanced(campaign: dict, audience: str) -> tuple:
    obj = b.GenerateBalancedTier(
        campaign_name=campaign["name"], year=campaign["year"],
        agency=campaign["agency"], brief=campaign["brief"],
        original_audience=audience,
    )
    return "balanced", _tier_to_dict(obj)


def _run_bold(campaign: dict, audience: str) -> tuple:
    # Bold uses Opus — wired in campaign_tiers.baml
    obj = b.GenerateBoldTier(
        campaign_name=campaign["name"], year=campaign["year"],
        agency=campaign["agency"], brief=campaign["brief"],
        original_audience=audience,
    )
    return "bold", _tier_to_dict(obj)


def run_tiers_in_parallel(campaign: dict, audience_str: str) -> dict:
    """
    Fan out Conservative / Balanced / Bold concurrently.
    Returns {conservative: dict, balanced: dict, bold: dict}.
    """
    print(f"  ⚡ Parallel tiers: {campaign['name']}")
    results = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futures = {
            ex.submit(_run_conservative, campaign, audience_str): "conservative",
            ex.submit(_run_balanced,     campaign, audience_str): "balanced",
            ex.submit(_run_bold,         campaign, audience_str): "bold",
        }
        for future in concurrent.futures.as_completed(futures):
            tier_label = futures[future]
            try:
                _, data = future.result()
                results[tier_label] = data
                print(f"     ✅ {tier_label.capitalize()} done")
            except Exception as e:
                print(f"     ⚠️  {tier_label} failed: {e}")
                results[tier_label] = {}

    return results


def generate_visual_prompts(campaign: dict, tiers: dict) -> dict:
    """Generate VisualPrompt for each tier in parallel."""
    prompts = {}

    def _one(tier_name: str, tier_data: dict) -> tuple:
        if not tier_data:
            return tier_name, {}
        obj = b.GenerateVisualPrompt(
            campaign_name=campaign["name"],
            tier=tier_data.get("tier_name", tier_name),
            concept=tier_data.get("concept", ""),
            visual_direction=tier_data.get("visual_direction", ""),
        )
        return tier_name, _visual_prompt_to_dict(obj)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futures = [ex.submit(_one, name, data) for name, data in tiers.items()]
        for future in concurrent.futures.as_completed(futures):
            name, data = future.result()
            prompts[name] = data

    return prompts
