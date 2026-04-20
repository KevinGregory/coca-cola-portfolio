# research.py
# Borrowed pattern from Alfred (github.com/KevinGregory/alfred).
#
# Alfred uses a web_search tool loop to build a live research dossier
# before generating any campaigns. We've adapted that exact pattern here:
# Claude calls web_search in a loop (up to MAX_SEARCH_CALLS times) until
# it has enough context, then returns a structured CampaignDossier.
#
# This replaces our hardcoded campaign.brief strings with real live research.

import os
import json
import anthropic

# Max number of web searches Claude can make per campaign.
# Alfred caps at ~8; we match that to control cost.
MAX_SEARCH_CALLS = 8

RESEARCH_SYSTEM_PROMPT = """
You are a senior advertising strategist and cultural historian.
Your job is to research a Coca-Cola advertising campaign in depth using web search.

For the given campaign, search for:
1. The original creative brief and agency background
2. Cultural context of the era (what was happening in society)
3. Reception and impact — awards, sales data, cultural legacy
4. Key creative decisions — casting, music, visual direction
5. How it was criticized or could have been stronger

Search multiple times until you have enough to write a thorough dossier.
When you have enough information, respond with DONE and a JSON summary like:
{
  "cultural_context": "...",
  "reception": "...",
  "creative_decisions": "...",
  "legacy": "...",
  "criticisms": "..."
}
""".strip()


def research_campaign(campaign: dict) -> dict:
    """
    Run a web_search agent loop for one campaign.
    Returns an enriched dict with real researched context added.

    If ANTHROPIC_API_KEY is not set or web search fails,
    falls back gracefully to the hardcoded brief.
    """
    print(f"  🔎 Researching: {campaign['name']} ({campaign['year']})...")

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    # The web_search tool — same tool Alfred uses
    tools = [
        {
            "type": "web_search_20250305",
            "name": "web_search",
        }
    ]

    messages = [
        {
            "role": "user",
            "content": (
                f"Research the Coca-Cola campaign '{campaign['name']}' "
                f"from {campaign['year']} by {campaign['agency']}. "
                f"Original brief: {campaign['brief']}"
            ),
        }
    ]

    researched_data = {}
    search_count = 0

    try:
        while search_count < MAX_SEARCH_CALLS:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                system=RESEARCH_SYSTEM_PROMPT,
                tools=tools,
                messages=messages,
            )

            # Add Claude's response to the message history
            messages.append({"role": "assistant", "content": response.content})

            # If Claude stopped naturally (no more tool calls), parse the final text
            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text") and "DONE" in block.text:
                        # Extract the JSON summary from Claude's response
                        try:
                            json_start = block.text.find("{")
                            json_end = block.text.rfind("}") + 1
                            if json_start >= 0 and json_end > json_start:
                                researched_data = json.loads(
                                    block.text[json_start:json_end]
                                )
                        except json.JSONDecodeError:
                            pass
                break

            # If Claude wants to use web_search, process the tool calls
            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use" and block.name == "web_search":
                        search_count += 1
                        print(f"     Search {search_count}: {block.input.get('query', '')[:60]}")
                        # The web_search tool returns results automatically —
                        # we just need to pass tool_result back with the block id
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": "Search executed.",
                            }
                        )

                if tool_results:
                    messages.append({"role": "user", "content": tool_results})
            else:
                break

    except Exception as e:
        print(f"     ⚠️  Research failed ({e}), using static brief.")

    # Merge research findings into the campaign dict
    enriched = dict(campaign)
    if researched_data:
        enriched["researched_context"] = researched_data
        enriched["brief"] = (
            campaign["brief"]
            + "\n\nResearched context: "
            + researched_data.get("cultural_context", "")
        )
        print(f"     ✅ Research complete ({search_count} searches)")
    else:
        print(f"     ℹ️  Using static brief (no live research data)")

    return enriched
