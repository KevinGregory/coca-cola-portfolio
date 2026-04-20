// campaign_tiers.baml
// Borrowed pattern from Alfred (github.com/KevinGregory/alfred).
//
// Alfred generates three campaign directions in parallel:
//   Conservative — play to existing brand equity
//   Balanced     — one fresh mechanic, still on-brand
//   Bold         — stunt-worthy, PR-bait, Opus-powered
//
// We've adapted this for campaign improvement proposals:
// each tier proposes a different strategic direction for
// reimagining the original Coca-Cola campaign today.

// ── Data classes ──

// One improvement direction for a campaign
class CampaignTier {
  tier_name string           // "Conservative" | "Balanced" | "Bold"
  tagline string             // New campaign tagline (≤8 words)
  headline string            // Hero ad headline
  concept string             // The big idea in 2-3 sentences
  visual_direction string    // Art direction notes
  media_strategy string      // Where and how to run it
  target_shift string        // Any audience expansion or shift
  risk_level string          // Low / Medium / High
  why_it_works string        // Strategic rationale
}

// All three tiers for one campaign
class CampaignTiers {
  conservative CampaignTier
  balanced CampaignTier
  bold CampaignTier
}

// Visual prompt for image generation (stub SVG or gpt-image-1)
class VisualPrompt {
  image_prompt string        // Detailed prompt for image generation
  color_palette string[]     // Hex colors to use
  mood_words string[]        // e.g. ["cinematic", "warm", "nostalgic"]
  composition string         // e.g. "wide establishing shot", "close-up portrait"
}

// ── Functions ──
// Clients (SonnetClient, OpusClient) are defined in clients.baml

// Conservative tier — Sonnet — protect existing brand equity
function GenerateConservativeTier(
  campaign_name: string,
  year: int,
  agency: string,
  brief: string,
  original_audience: string
) -> CampaignTier {
  client SonnetClient
  prompt #"
    You are a senior brand strategist at a top ad agency.

    Your job: propose a Conservative reimagining of this Coca-Cola campaign.
    Conservative means: stay close to what made the original work. Modernize
    the execution but protect the emotional equity. Safe enough to present
    to a risk-averse CMO. No stunts, no controversy.

    Original campaign: {{ campaign_name }} ({{ year }})
    Agency: {{ agency }}
    Brief: {{ brief }}
    Original audience: {{ original_audience }}

    Return a single, concrete campaign direction. Be specific — name
    real platforms, real formats, real creative choices. No vague advice.

    Set tier_name to "Conservative" and risk_level to "Low".

    {{ ctx.output_format }}
  "#
}

// Balanced tier — Sonnet — one fresh mechanic, still on-brand
function GenerateBalancedTier(
  campaign_name: string,
  year: int,
  agency: string,
  brief: string,
  original_audience: string
) -> CampaignTier {
  client SonnetClient
  prompt #"
    You are a creative director at a top ad agency.

    Your job: propose a Balanced reimagining of this Coca-Cola campaign.
    Balanced means: introduce ONE bold mechanic or platform that the original
    couldn't have used, but keep the emotional core intact. Ambitious enough
    to win at Cannes, safe enough to actually get approved.

    Original campaign: {{ campaign_name }} ({{ year }})
    Agency: {{ agency }}
    Brief: {{ brief }}
    Original audience: {{ original_audience }}

    Name your fresh mechanic explicitly. Explain why it fits Coca-Cola.

    Set tier_name to "Balanced" and risk_level to "Medium".

    {{ ctx.output_format }}
  "#
}

// Bold tier — Opus — stunt-worthy, PR-bait, creative courage
function GenerateBoldTier(
  campaign_name: string,
  year: int,
  agency: string,
  brief: string,
  original_audience: string
) -> CampaignTier {
  client OpusClient
  prompt #"
    You are the most daring creative director in advertising.

    Your job: propose a Bold reimagining of this Coca-Cola campaign.
    Bold means: the kind of idea that gets the agency fired or wins the
    Grand Prix. PR-bait. Culturally disruptive. Something that will be
    discussed in ad school for years. It can be risky, strange, or
    provocative — but it must still be fundamentally true to Coca-Cola.

    Original campaign: {{ campaign_name }} ({{ year }})
    Agency: {{ agency }}
    Brief: {{ brief }}
    Original audience: {{ original_audience }}

    Swing hard. Justify the risk with a clear strategic rationale.

    Set tier_name to "Bold" and risk_level to "High".

    {{ ctx.output_format }}
  "#
}

// Generate an image prompt for a campaign tier
function GenerateVisualPrompt(
  campaign_name: string,
  tier: string,
  concept: string,
  visual_direction: string
) -> VisualPrompt {
  client SonnetClient
  prompt #"
    You are an art director writing a prompt for an AI image generator.

    Create a detailed image generation prompt for this campaign concept:

    Campaign: {{ campaign_name }}
    Tier: {{ tier }}
    Concept: {{ concept }}
    Visual direction: {{ visual_direction }}

    The image should work as a hero ad visual. No text in the image.
    Coca-Cola red (#E63946) should feature prominently.

    {{ ctx.output_format }}
  "#
}
