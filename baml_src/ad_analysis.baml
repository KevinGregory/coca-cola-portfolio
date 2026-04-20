// ad_analysis.baml
// This file defines the AI-powered functions for analyzing Coca-Cola ads.
// Each "class" is like a structured form that Claude fills out.
// Each "function" describes what to send to Claude and what shape to get back.

// ─────────────────────────────────────────────
// DATA CLASSES (the shape of each AI response)
// ─────────────────────────────────────────────

// Describes who the ad was made for
class AudienceResearch {
  primary_demographic string        // e.g. "Teens and young adults 13–24"
  psychographics string[]           // values, attitudes, lifestyle traits
  cultural_moment string            // what was happening in society at the time
  emotional_drivers string[]        // what emotions the campaign taps into
  geographic_focus string           // global, regional, or specific market
  media_channels string[]           // TV, print, digital, OOH, etc.
}

// Breaks down one section of an ad
class AdSection {
  section_name string               // e.g. "Headline", "Visuals", "CTA"
  current_execution string          // what the original ad actually does
  strengths string[]                // what works well
  weaknesses string[]               // what could be better
  improvement string                // specific rewrite or upgrade suggestion
  reasoning string                  // why this improvement would work
}

// Full analysis of a single ad
class AdSectionAnalysis {
  sections AdSection[]              // array of section breakdowns
  overall_tone string               // e.g. "Nostalgic, warm, inclusive"
  brand_alignment_score int         // 1–10: how well it fits Coca-Cola's brand
  brand_alignment_notes string      // explanation of the score
}

// Improvement recommendations for the whole campaign
class AdImprovements {
  headline_rewrite string           // rewritten headline
  visual_direction string           // art direction notes
  cta_rewrite string                // rewritten call to action
  tone_adjustment string            // how to shift the tone
  modern_relevance string           // how to make it feel fresh today
  audience_expansion string         // how to reach a broader/new audience
  platform_adaptations string[]     // how to adapt it for TikTok, Instagram, etc.
}

// High-level portfolio summary for a campaign
class CampaignSummary {
  strategic_insight string          // the big idea behind the campaign
  why_it_worked string              // the reason it succeeded
  cultural_legacy string            // its lasting impact
  portfolio_talking_points string[] // what to say about it in a job interview
  skills_demonstrated string[]      // creative skills this project shows
}

// ─────────────────────────────────────────────
// BAML FUNCTIONS (what we call from Python)
// ─────────────────────────────────────────────

// Researches the target audience for a campaign
function ResearchAudience(
  campaign_name: string,
  agency: string,
  year: int,
  brief: string
) -> AudienceResearch {
  client ClaudeClient
  prompt #"
    You are a senior advertising strategist and cultural analyst.

    Analyze the target audience for this Coca-Cola campaign:

    Campaign: {{ campaign_name }}
    Agency: {{ agency }}
    Year: {{ year }}
    Brief: {{ brief }}

    Research and describe the audience with depth and specificity.
    Consider the cultural and social context of {{ year }}.

    {{ ctx.output_format }}
  "#
}

// Analyzes each section of the ad
function AnalyzeAdSections(
  campaign_name: string,
  year: int,
  ad_description: string
) -> AdSectionAnalysis {
  client ClaudeClient
  prompt #"
    You are a senior creative director at a top ad agency.

    Analyze this Coca-Cola ad section by section:

    Campaign: {{ campaign_name }}
    Year: {{ year }}
    Ad Description: {{ ad_description }}

    Break it down into sections: Headline, Tagline, Visuals, Color Palette,
    Music/Sound, Talent/Casting, Call to Action, and Brand Logo Usage.

    For each section, identify what works, what doesn't, and a specific improvement.

    {{ ctx.output_format }}
  "#
}

// Generates specific improvement recommendations
function GenerateImprovements(
  campaign_name: string,
  year: int,
  audience: string,
  current_weaknesses: string
) -> AdImprovements {
  client ClaudeClient
  prompt #"
    You are a creative director and brand strategist.

    Generate specific, actionable improvements for this Coca-Cola campaign:

    Campaign: {{ campaign_name }}
    Original Year: {{ year }}
    Target Audience: {{ audience }}
    Current Weaknesses: {{ current_weaknesses }}

    Provide concrete rewrites and suggestions — not vague advice.
    Think about how to make this campaign stronger today while respecting the original vision.

    {{ ctx.output_format }}
  "#
}

// Generates portfolio-ready talking points
function SummarizeCampaign(
  campaign_name: string,
  agency: string,
  year: int,
  brief: string,
  analysis_summary: string
) -> CampaignSummary {
  client ClaudeClient
  prompt #"
    You are an advertising professor and portfolio coach helping a junior creative
    build their first portfolio.

    Summarize this Coca-Cola campaign for a job-application portfolio:

    Campaign: {{ campaign_name }}
    Agency: {{ agency }}
    Year: {{ year }}
    Brief: {{ brief }}
    Analysis: {{ analysis_summary }}

    Focus on what makes this campaign worth studying and what skills analyzing it demonstrates.

    {{ ctx.output_format }}
  "#
}
