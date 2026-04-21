// Turns the raw web-research blob into a structured brief a creative director could skim.

class CompanyDossier {
  name           string                @description("Canonical company name as it appears in marketing materials")
  one_liner      string                @description("One sentence, how the company describes itself")
  industry       string
  products       string[]              @description("Main products or service lines")
  brand_voice    string                @description("Adjectives: 'irreverent', 'premium/minimal', 'engineer-tone', 'homey/handmade'")
  positioning    string                @description("How the brand is currently positioned against competitors")
  competitors    string[]
  recent_news    string[]              @description("Launches, campaigns, earnings moments, PR events from the last 12 months")
  audience_hints string[]              @description("Demographics, psychographics, or use cases that keep appearing in the research")
  opportunities  string[]              @description("Advertising angles a creative director would latch onto — cultural moments, unmet needs, category conventions to break")
  sources        string[]              @description("URLs that were cited by web_search during research")
}

// Map step in the map-reduce: Gemini compresses a chunk of raw research into
// a tight, bulleted fact-list. The goal is to aggressively shed tokens before
// the final dossier call — keep only what a creative director could actually use.
function SummarizeResearchChunk(company_name: string, chunk: string) -> string {
  client GeminiFlash
  prompt #"
    Extract the KEY FACTS about {{ company_name }} from the chunk below, as
    compact bullet points.

    Rules:
    - Output ONLY bullet points (one fact per line, starting with "- ").
    - Each bullet: 1 short sentence. No sub-bullets. No paragraphs. No preamble.
    - HARD CEILING: 15 bullets max for this chunk.
    - Keep: product names, dollar figures, dates, people's names, specific campaign
      names, competitor names, taglines, cultural moments, controversies, quotes.
    - Drop: marketing fluff, generic category statements, anything speculative,
      anything repeated elsewhere.

    Chunk:
    ---
    {{ chunk }}
    ---
  "#
}

// Reduce step: take all chunk bullet-lists and produce a single dossier-ready
// briefing under a hard size cap. This is what actually gets handed to Claude.
function CondenseToBriefing(company_name: string, mapped_bullets: string) -> string {
  client GeminiFlash
  prompt #"
    You have a bulleted fact-list about {{ company_name }} from multiple research chunks.
    Consolidate into a single briefing for an advertising agency's creative team.

    Rules:
    - Dedupe aggressively — if two bullets say the same thing, keep the most specific.
    - HARD CEILING: 40 bullet points total, ~1500 characters total output.
    - Group loosely by: What they do / How they're positioned / Audience / Competitors /
      Recent moments / Cultural angles. Use plain-text section headers (one line each) like
      'Positioning:' or 'Audience:' followed by bullets.
    - Every bullet still starts with "- ". Keep specificity — names, numbers, quotes.
    - No preamble, no closing remark.

    Mapped bullets:
    ---
    {{ mapped_bullets }}
    ---
  "#
}

function ExtractDossier(company_name: string, raw_research: string, sources: string[]) -> CompanyDossier {
  client ClaudeSonnet
  prompt #"
    You are a strategist at an advertising agency reading a research dossier for a new-business pitch.

    Company: {{ company_name }}

    Extract a structured dossier from the raw research below. Be specific — avoid generic filler like
    "they care about quality" or "target audience is millennials." Pull real details, real competitors,
    real cultural moments.

    For `opportunities`, think like a creative director: what's the cultural angle, the category
    convention ripe to break, the tension this brand could own?

    Raw research:
    ---
    {{ raw_research }}
    ---

    Sources already captured (use as-is for the sources field):
    {{ sources }}

    {{ ctx.output_format }}
  "#
}

test liquid_death_dossier {
  functions [ExtractDossier]
  args {
    company_name "Liquid Death"
    raw_research #"
      Liquid Death is a canned water brand founded in 2017 by Mike Cessario, a former creative director.
      Sold in tallboy cans that mimic beer cans. Positioning: "murder your thirst." Major competitors
      include Aquafina, Dasani, Essentia. Notable campaigns: Martha Stewart partnership, "Greatest Hates"
      album of negative reviews read aloud by celebrities, severed hand in pool stunt. Recent 2025 news:
      launched iced tea line, crossed $300M revenue, rumored IPO. Distributed in 7-Eleven, Whole Foods,
      tattoo parlors, skate parks. Appeal skews Gen Z + millennial men but has broken through to general.
      Known for heavy-metal aesthetic, irreverent long-form content on TikTok/YouTube.
    "#
    sources ["https://liquiddeath.com", "https://en.wikipedia.org/wiki/Liquid_Death"]
  }
}
