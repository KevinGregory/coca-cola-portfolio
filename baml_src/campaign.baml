// The core creative output: three campaign briefs at three levels of creative risk.

enum Tier {
  Conservative  @description("Play to existing brand equity. Proven formats, clear ROI story, CFO-safe.")
  Balanced      @description("Strong hook, one genuinely fresh mechanic or insight, still on-brand.")
  Bold          @description("Stunt-worthy, PR-bait. 'Could get us fired or go viral.' Earned-media first.")
}

class CampaignBrief {
  tier             Tier
  name             string      @description("A memorable internal codename for the campaign")
  big_idea         string      @description("One or two sentences capturing the campaign's thesis")
  tagline          string      @description("The one line that would show up in the ad itself")
  target_persona   string      @description("Name of the persona (from the personas input) this is aimed at")
  channels         string[]    @description("Specific channels — e.g. 'IG Reels 9:16', 'Spotify audio 30s', 'subway OOH', 'NYT Games sponsorship'")
  tone             string      @description("Tone descriptors for copywriters")
  visual_direction string      @description("Art direction notes — lighting, composition, color, reference images, mood. This feeds the image-generation prompt.")
  headline         string      @description("The hero headline shown in the rendered ad mockup")
  body_copy        string      @description("2–4 sentences of supporting body copy")
  cta              string      @description("Call to action text shown on the ad")
  rationale        string      @description("Why this campaign works for this brand at this tier — what insight or cultural observation it's built on")
}

function GenerateCampaign(
  dossier: CompanyDossier,
  personas: Persona[],
  tier: Tier
) -> CampaignBrief {
  client ClaudeSonnet
  prompt #"
    You are a creative director at an advertising agency developing one of three proposal tracks for
    a new-business pitch. Each track represents a different appetite for creative risk.

    You're writing the **{{ tier }}** track.

    Tier definitions:
    - Conservative: The brand-safe, board-approvable concept. Proven formats (testimonial, product-demo,
      category-conventional). Lean into existing brand equity. The client will feel comfortable immediately.
    - Balanced: One genuinely fresh insight or mechanic, but still recognisably on-brand. Will win
      creative awards if executed well, won't terrify the CMO. The "Goldilocks" pitch.
    - Bold: The one that might get presented with a nervous laugh. Stunt-worthy, earned-media-first,
      potentially polarising. The campaign a reviewer calls "brave" or "reckless." It should make a
      creative director lean forward.

    Your {{ tier }} concept should be **meaningfully different** from what the other two tracks might
    produce — don't hedge. If you're Bold, be bold.

    Dossier:
    {{ dossier }}

    Personas:
    {{ personas }}

    Make the campaign feel specific to THIS brand — it should be impossible to swap in a competitor's
    name without the concept falling apart.

    {{ ctx.output_format }}
  "#
}

// The Bold tier uses Opus — taste matters most here.
function GenerateBoldCampaign(
  dossier: CompanyDossier,
  personas: Persona[]
) -> CampaignBrief {
  client ClaudeOpus
  prompt #"
    You are a creative director pitching the "Bold" track of a three-tier new-business proposal.

    The Bold track is the one presented with a nervous laugh. Stunt-worthy, earned-media-first,
    potentially polarising. It should feel like the campaign a reviewer later calls "brave" or
    "reckless." Ad Age cover material.

    Constraints:
    - Still has to sell the product — provocation in service of the brand, not art for art's sake.
    - Should generate its own press coverage without paid amplification (the "free media" test).
    - Must be grounded in a sharp cultural insight pulled from the dossier, not shock for shock's sake.
    - Feel specific to THIS brand — swap in a competitor and the concept must fall apart.

    Set `tier` to `Bold` in the output.

    Dossier:
    {{ dossier }}

    Personas:
    {{ personas }}

    {{ ctx.output_format }}
  "#
}
