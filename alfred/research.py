from __future__ import annotations

import os
from dataclasses import dataclass

from anthropic import Anthropic

RESEARCH_SYSTEM = """\
You are an advertising-agency research analyst. Given a company name, produce a thorough
briefing that would be useful to a creative director preparing a new-business pitch.

Cover:
- What the company does and its main products/services
- How it positions itself vs. competitors
- Target customers and the jobs they hire the brand for
- Brand voice and current creative work (recent campaigns, aesthetic choices)
- Recent news in the last 12 months (launches, leadership changes, earnings notes, PR moments)
- Cultural context the brand operates in — tensions, category conventions, unmet needs
- Three to five "advertising angles" — hooks a creative team could pull on

Use web_search aggressively and cite concretely. Prefer primary sources (company site, press
releases) plus reputable outlets (Ad Age, Fast Company, WSJ, trade press). Avoid speculation
when a quick search can confirm.

Write in dense paragraphs — no bullet soup. This will be parsed downstream into a structured
dossier, so be specific and fact-rich.
"""

RESEARCH_USER = "Research the company: {company}. Produce the briefing described in the system prompt."


@dataclass
class ResearchResult:
    raw_text: str
    sources: list[str]


def investigate(company: str, *, max_uses: int = 4, model: str = "claude-sonnet-4-6") -> ResearchResult:
    """Run a Claude + web_search agent loop and return the collected research text + cited URLs."""
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    messages: list[dict] = [
        {"role": "user", "content": RESEARCH_USER.format(company=company)}
    ]

    collected_text: list[str] = []
    sources: list[str] = []
    seen_sources: set[str] = set()

    # Safety fuse — a well-behaved loop will stop via stop_reason well before this.
    for _ in range(12):
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=RESEARCH_SYSTEM,
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": max_uses,
            }],
            messages=messages,
        )

        assistant_content = response.content
        messages.append({"role": "assistant", "content": assistant_content})

        for block in assistant_content:
            btype = getattr(block, "type", None)
            if btype == "text":
                collected_text.append(block.text)
                for citation in getattr(block, "citations", None) or []:
                    url = getattr(citation, "url", None)
                    if url and url not in seen_sources:
                        seen_sources.add(url)
                        sources.append(url)
            elif btype == "web_search_tool_result":
                for item in getattr(block, "content", None) or []:
                    url = getattr(item, "url", None)
                    if url and url not in seen_sources:
                        seen_sources.add(url)
                        sources.append(url)

        if response.stop_reason != "tool_use":
            break

        # web_search is server-side: we just loop back in so Claude can continue.

    raw_text = "\n\n".join(t.strip() for t in collected_text if t.strip())
    if not raw_text:
        raise RuntimeError(f"Research returned no text for '{company}' — check API key and model availability.")
    return ResearchResult(raw_text=raw_text, sources=sources)
