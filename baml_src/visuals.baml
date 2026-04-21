// Two steps: author an image-gen prompt from the campaign, then compose the ad mockup as HTML.

class VisualPrompt {
  prompt       string   @description("A single-paragraph image-generation prompt, lighting + composition + subject + style")
  aspect       string   @description("Exactly one of: '1:1', '4:5', '16:9', '9:16'")
  style_notes  string   @description("Short human-readable style descriptor — e.g. 'dark editorial, high-contrast, cinematic grain'")
}

function GenerateVisualPrompt(campaign: CampaignBrief) -> VisualPrompt {
  client ClaudeSonnet
  prompt #"
    Translate the campaign's visual_direction into a prompt suitable for a state-of-the-art
    image generator (gpt-image-1 or Flux). Focus on:
    - Subject + scene composition
    - Lighting and mood
    - Style reference (editorial, documentary, surreal, cel-shaded, etc)
    - What to avoid (no text overlay — text will be rendered separately in HTML)

    Pick an aspect ratio that matches the primary channel (1:1 for feed, 4:5 for IG, 16:9 for YT/OOH, 9:16 for stories/Reels).

    Campaign:
    {{ campaign }}

    {{ ctx.output_format }}
  "#
}

class AdMockup {
  html  string  @description("Self-contained HTML+inline CSS snippet rendering one ad unit")
}

function RenderAdHTML(campaign: CampaignBrief, image_src: string) -> AdMockup {
  client ClaudeSonnet
  prompt #"
    Compose a single self-contained HTML fragment that renders this campaign as a polished ad mockup.

    Rules:
    - Root element: `<div class="ad-card ad-{{ campaign.tier }}">` — nothing outside.
    - Use INLINE styles only (no <style>, no <link>, no <script>).
    - Include the background image using `image_src` as-is (relative path, usable in an <img> or
      as a CSS background-image). Do NOT change the path.
    - Layout: full-bleed image on top or background, tagline/headline overlaid or below, CTA button.
    - Feel like a real ad unit — strong typographic hierarchy, plenty of whitespace, good contrast
      for legibility over the image (scrim/gradient overlay if needed).
    - Target aspect: roughly 4:5 or 1:1. Max width 480px. Box-shadow ok.
    - Use system font stack. Do not import external fonts.
    - Tier-appropriate feel: Conservative = clean and trustworthy, Balanced = confident and modern,
      Bold = loud, possibly asymmetric, rule-breaking typography.

    Campaign:
    {{ campaign }}

    image_src: {{ image_src }}

    Return ONLY the HTML fragment in the `html` field.

    {{ ctx.output_format }}
  "#
}
