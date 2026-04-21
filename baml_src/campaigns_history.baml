class PastCampaign {
  name         string    @description("Campaign name — e.g. 'Share a Coke', 'Real Beauty'")
  years        string    @description("Year or range — e.g. '2014', '2011–present'. 'Unknown' if not found.")
  concept      string    @description("2–3 sentences: the big idea, execution mechanic, what made it distinctive")
  channels     string[]  @description("Where it ran — TV, OOH, social platform, experiential, etc.")
  outcome      string    @description("Reported results, cultural impact, or award wins. 'Not reported' if nothing found.")
  significance string    @description("Why this campaign matters for understanding how this brand communicates")
}

function AnalyzePastCampaigns(company_name: string, raw_research: string) -> PastCampaign[] {
  client ClaudeSonnetLong
  prompt #"
    You are a senior advertising strategist building a campaign-history reference for a new-business pitch.

    Company: {{ company_name }}

    From the research below, identify the most significant ad campaigns this company has run historically.
    Focus on named campaigns, award winners, viral moments, brand-defining work, or infamous misfires.
    Ignore generic product launches unless they had a distinct creative campaign attached.

    Extract between 2 and 6 campaigns. If fewer than 2 are identifiable, return what is found.
    Do not fabricate campaigns not present in the research.

    Pull concrete details — actual taglines, channel specifics, reported outcomes, cultural context.
    Vague entries ("they ran a TV campaign in 2019") are not useful.

    Raw research:
    ---
    {{ raw_research }}
    ---

    {{ ctx.output_format }}
  "#
}
