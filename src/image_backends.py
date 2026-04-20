# image_backends.py
# Borrowed pattern from Alfred (github.com/KevinGregory/alfred).
#
# Alfred supports three image backends: openai, replicate, and stub.
# The stub backend generates an inline SVG so the full pipeline works
# with zero API keys — the code is demo-able anywhere.
#
# We've adapted this for the portfolio: each campaign gets a visual
# "ad mockup" SVG generated without needing any image API.

import os
import hashlib


# ── Stub backend ── generates deterministic SVG ad mockups
# This is what Alfred uses when ALFRED_IMAGE_BACKEND=stub.
# Perfect for portfolio demos — no OpenAI or Replicate key needed.


COKE_RED = "#E63946"
COKE_DARK = "#1A1A2E"
COKE_CREAM = "#FFF8F0"

# A small set of visual layouts — each campaign gets one based on its era
LAYOUT_STYLES = {
    "buy_the_world": {
        "bg": "#4A7C59",          # earthy green — 70s outdoors
        "accent": COKE_RED,
        "mood": "Unity · Peace · 1971",
        "shape": "crowd",
    },
    "share_a_coke": {
        "bg": COKE_RED,
        "accent": "white",
        "mood": "Personalization · 2011",
        "shape": "bottle",
    },
    "holidays_coming": {
        "bg": "#0A0A1A",          # dark winter night
        "accent": COKE_RED,
        "mood": "Magic · Christmas · 1995",
        "shape": "trucks",
    },
    "open_happiness": {
        "bg": "#FFD700",          # bright yellow — optimism
        "accent": COKE_RED,
        "mood": "Open Happiness · 2009",
        "shape": "vending",
    },
    "real_magic": {
        "bg": "#0D0D0D",          # dark — gaming aesthetic
        "accent": COKE_RED,
        "mood": "Real Magic · Gen Z · 2021",
        "shape": "gaming",
    },
}

DEFAULT_STYLE = {
    "bg": COKE_RED,
    "accent": "white",
    "mood": "Coca-Cola",
    "shape": "bottle",
}


def generate_stub_svg(campaign: dict) -> str:
    """
    Generate an inline SVG ad mockup for a campaign.
    No API key required — runs fully offline.

    Returns an SVG string you can embed directly in HTML.
    """
    style = LAYOUT_STYLES.get(campaign["id"], DEFAULT_STYLE)
    name = campaign["name"]
    year = str(campaign["year"])
    agency = campaign["agency"]
    shape = style["shape"]

    # Build the visual element based on campaign shape type
    visual_element = _build_shape(shape, style)

    svg = f"""<svg viewBox="0 0 400 260" xmlns="http://www.w3.org/2000/svg" width="400" height="260">
  <rect width="400" height="260" fill="{style['bg']}"/>
  {visual_element}
  <text x="200" y="190" font-family="Georgia,serif" font-size="18" font-style="italic"
        fill="white" text-anchor="middle" opacity="0.95">{_escape(name)}</text>
  <text x="200" y="212" font-family="Arial,sans-serif" font-size="10"
        fill="white" text-anchor="middle" opacity="0.55" text-transform="uppercase"
        letter-spacing="2">{agency.upper()} · {year}</text>
  <text x="200" y="240" font-family="Arial,sans-serif" font-size="9"
        fill="white" text-anchor="middle" opacity="0.35">{style['mood']}</text>
  <rect x="160" y="248" width="80" height="2" rx="1" fill="{style['accent']}" opacity="0.4"/>
</svg>"""

    return svg


def _escape(text: str) -> str:
    """Escape XML special characters for SVG text."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;")


def _build_shape(shape: str, style: dict) -> str:
    """Return the SVG visual element for a given shape type."""
    acc = style["accent"]

    if shape == "crowd":
        # Silhouette of people on a hill — 1971 Hilltop ad
        return f"""
  <ellipse cx="200" cy="155" rx="160" ry="40" fill="{acc}" opacity="0.08"/>
  <g opacity="0.6">
    {"".join([f'<rect x="{120+i*20}" y="{130-abs(i-6)*3}" width="8" height="25" rx="4" fill="white" opacity="0.5"/>' for i in range(9)])}
  </g>
  <ellipse cx="200" cy="130" rx="80" ry="6" fill="{acc}" opacity="0.15"/>"""

    elif shape == "bottle":
        # Stylized Coke bottle silhouette
        return f"""
  <path d="M185 60 L180 80 L175 100 L173 140 L175 170 L225 170 L227 140 L225 100 L220 80 L215 60 Z"
        fill="white" opacity="0.15" rx="4"/>
  <path d="M188 60 L183 80 L178 100 L176 140 L178 165 L222 165 L224 140 L222 100 L217 80 L212 60 Z"
        fill="white" opacity="0.1"/>
  <text x="200" y="125" font-family="Georgia,serif" font-size="22" font-style="italic"
        fill="white" text-anchor="middle" opacity="0.9">Share a</text>
  <text x="200" y="150" font-family="Georgia,serif" font-size="14" font-style="italic"
        fill="white" text-anchor="middle" opacity="0.7">Coke with</text>
  <text x="200" y="165" font-family="Georgia,serif" font-size="11"
        fill="white" text-anchor="middle" opacity="0.5">Sarah</text>"""

    elif shape == "trucks":
        # Illuminated trucks — Christmas 1995
        return f"""
  {"".join([f'<rect x="{60+i*90}" y="{100}" width="70" height="35" rx="4" fill="{COKE_RED}" opacity="0.9"/><rect x="{63+i*90}" y="103" width="64" height="29" rx="2" fill="{COKE_RED}"/><circle cx="{80+i*90}" cy="138" r="6" fill="#333"/><circle cx="{113+i*90}" cy="138" r="6" fill="#333"/>' for i in range(3)])}
  <g opacity="0.4">
    {"".join([f'<line x1="{95+i*90}" y1="80" x2="{95+i*90}" y2="100" stroke="white" stroke-width="1" opacity="0.3"/>' for i in range(3)])}
  </g>
  <text x="200" y="78" font-family="Georgia,serif" font-size="13" font-style="italic"
        fill="white" text-anchor="middle" opacity="0.65" letter-spacing="2">Holidays are coming...</text>"""

    elif shape == "vending":
        # Vending machine — Open Happiness 2009
        return f"""
  <rect x="150" y="60" width="100" height="130" rx="6" fill="{COKE_RED}" opacity="0.8"/>
  <rect x="155" y="65" width="90" height="70" rx="4" fill="white" opacity="0.12"/>
  <text x="200" y="108" font-family="Georgia,serif" font-size="14" font-style="italic"
        fill="white" text-anchor="middle">Open</text>
  <text x="200" y="126" font-family="Georgia,serif" font-size="14" font-style="italic"
        fill="white" text-anchor="middle">Happiness</text>
  <rect x="160" y="145" width="80" height="20" rx="3" fill="white" opacity="0.2"/>
  <circle cx="200" cy="170" r="8" fill="white" opacity="0.3"/>"""

    elif shape == "gaming":
        # Gaming controller silhouette — Real Magic 2021
        return f"""
  <rect x="130" y="90" width="140" height="80" rx="24" fill="#1A1A1A" stroke="white" stroke-width="1" opacity="0.6"/>
  <circle cx="165" cy="120" r="14" fill="#111" opacity="0.8"/>
  <circle cx="235" cy="120" r="14" fill="#111" opacity="0.8"/>
  <circle cx="163" cy="118" r="4" fill="{COKE_RED}"/>
  <circle cx="175" cy="108" r="4" fill="#4488FF"/>
  <circle cx="163" cy="130" r="4" fill="#44DD88"/>
  <circle cx="153" cy="120" r="4" fill="#FFAA00"/>
  <text x="200" y="155" font-family="Arial,sans-serif" font-size="9"
        fill="white" text-anchor="middle" opacity="0.3" letter-spacing="3">ONE COKE AWAY FROM EACH OTHER</text>"""

    # Fallback — generic Coke can shape
    return f'<rect x="175" y="80" width="50" height="80" rx="8" fill="white" opacity="0.15"/>'


def get_backend():
    """Return the active image backend name from env, defaulting to stub."""
    return os.environ.get("COCA_IMAGE_BACKEND", "stub").lower()


def generate_campaign_visual(campaign: dict) -> str:
    """
    Main entry point — returns an image for a campaign.

    backend=stub  → inline SVG (default, no API key needed)
    backend=openai → gpt-image-1 (requires OPENAI_API_KEY)
    """
    backend = get_backend()

    if backend == "stub":
        return generate_stub_svg(campaign)

    elif backend == "openai":
        return _generate_openai_image(campaign)

    else:
        print(f"  ⚠️  Unknown backend '{backend}', falling back to stub.")
        return generate_stub_svg(campaign)


def _generate_openai_image(campaign: dict) -> str:
    """
    Generate an ad image using OpenAI's gpt-image-1.
    Requires OPENAI_API_KEY. Returns a data URI string.
    """
    try:
        import openai
        import base64

        client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        prompt = (
            f"A cinematic advertising photograph for Coca-Cola's '{campaign['name']}' campaign "
            f"from {campaign['year']} by {campaign['agency']}. "
            f"Style: {campaign.get('brief', '')[:200]}. "
            f"Coca-Cola red color palette. No text in image. Professional ad photography."
        )

        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x640",
            quality="medium",
            n=1,
        )

        # Return as inline data URI so it works in self-contained HTML
        image_data = response.data[0].b64_json
        return f'<img src="data:image/png;base64,{image_data}" style="width:100%;height:100%;object-fit:cover"/>'

    except Exception as e:
        print(f"  ⚠️  OpenAI image failed ({e}), falling back to stub.")
        return generate_stub_svg(campaign)
