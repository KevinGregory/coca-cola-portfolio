// Claude clients for Alfred.
// Sonnet for most work (fast + cheap + smart enough).
// Opus for the "Bold" creative tier where taste matters most.

client<llm> ClaudeSonnet {
  provider anthropic
  options {
    model "claude-sonnet-4-6"
    api_key env.ANTHROPIC_API_KEY
    // Kept modest on purpose: Anthropic rate-limits count RESERVED output tokens
    // against the input-TPM budget, so a smaller cap here reduces 429s on lower tiers.
    max_tokens 2048
  }
}

// Higher output cap for structured extraction tasks that produce longer arrays.
client<llm> ClaudeSonnetLong {
  provider anthropic
  options {
    model "claude-sonnet-4-6"
    api_key env.ANTHROPIC_API_KEY
    max_tokens 4096
  }
}

client<llm> ClaudeOpus {
  provider anthropic
  options {
    model "claude-opus-4-7"
    api_key env.ANTHROPIC_API_KEY
    max_tokens 4096
  }
}

// Gemini 2.5 Flash — cheap, fast, huge context. Used for the map-reduce
// summarization pass that compresses raw research before it hits Claude,
// which keeps us under Anthropic's input-TPM limits on lower API tiers.
client<llm> GeminiFlash {
  provider google-ai
  options {
    model "gemini-2.5-flash"
    api_key env.GOOGLE_API_KEY
  }
}

generator python_generator {
  output_type "python/pydantic"
  output_dir "../"
  version "0.221.0"
  default_client_mode sync
}
