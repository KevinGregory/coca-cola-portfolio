// clients.baml
// Single source of truth for all AI clients used across this project.
// BAML reads ANTHROPIC_API_KEY automatically from the environment.
//
// Client routing (borrowed from Alfred):
//   ClaudeClient  — default for all analysis functions (Sonnet, fast + cheap)
//   SonnetClient  — Conservative + Balanced campaign tiers
//   OpusClient    — Bold tier only (taste matters most on risky creative)

// Required: tells baml-cli generate where to write the Python client
generator target {
  output_type "python/pydantic"
  output_dir "../baml_client"
  version "0.75.0"
}

client<llm> ClaudeClient {
  provider anthropic
  options {
    model "claude-sonnet-4-20250514"
    max_tokens 4096
  }
}

client<llm> SonnetClient {
  provider anthropic
  options {
    model "claude-sonnet-4-20250514"
    max_tokens 2048
  }
}

// Alfred's key insight: use the best model only where taste matters most.
// Bold tier uses Opus — the extra cost is worth it for the riskiest creative.
client<llm> OpusClient {
  provider anthropic
  options {
    model "claude-opus-4-5"
    max_tokens 2048
  }
}
