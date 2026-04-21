// Two or three target audience personas distilled from the dossier.

class Persona {
  name         string   @description("A short, memorable label — e.g., 'Skeptical Dad', 'Post-gym Zillennial'")
  demographics string   @description("Age band, income range, geography, life stage")
  psychographics string @description("Values, fears, aspirations — the internal monologue, not just census data")
  media_diet   string[] @description("Where they spend attention: specific platforms, shows, creators, publications")
  jobs_to_be_done string[] @description("What they're trying to accomplish when they encounter this brand")
}

function IdentifyPersonas(dossier: CompanyDossier) -> Persona[] {
  client ClaudeSonnet
  prompt #"
    Based on the dossier below, produce 2 or 3 target audience personas for this brand's next
    advertising campaign. Personas should be distinct enough that a creative brief written for one
    wouldn't work for the others.

    Avoid generic demographics. Each persona should feel like a specific person a planner could
    picture — name them something evocative.

    Dossier:
    {{ dossier }}

    {{ ctx.output_format }}
  "#
}
