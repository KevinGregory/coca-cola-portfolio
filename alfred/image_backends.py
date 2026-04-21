from __future__ import annotations

import base64
import os
from abc import ABC, abstractmethod
from html import escape
from pathlib import Path

_ASPECT_TO_OPENAI_SIZE = {
    "1:1": "1024x1024",
    "4:5": "1024x1536",
    "16:9": "1536x1024",
    "9:16": "1024x1536",
}

_ASPECT_TO_WH = {
    "1:1": (1024, 1024),
    "4:5": (1024, 1280),
    "16:9": (1600, 900),
    "9:16": (900, 1600),
}


class ImageBackend(ABC):
    @abstractmethod
    def generate(self, prompt: str, aspect: str, out_path: Path) -> Path:
        """Generate an image and return its final path (may differ by extension)."""


class OpenAIImageBackend(ImageBackend):
    def __init__(self, model: str = "gpt-image-1"):
        from openai import OpenAI
        self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self._model = model

    def generate(self, prompt: str, aspect: str, out_path: Path) -> Path:
        size = _ASPECT_TO_OPENAI_SIZE.get(aspect, "1024x1024")
        resp = self._client.images.generate(
            model=self._model,
            prompt=prompt,
            size=size,
            n=1,
        )
        data = resp.data[0]
        png_bytes = base64.b64decode(data.b64_json) if data.b64_json else None
        if png_bytes is None and getattr(data, "url", None):
            import httpx
            png_bytes = httpx.get(data.url, timeout=60).content
        if not png_bytes:
            raise RuntimeError("OpenAI image response had neither b64_json nor url.")
        out_path = out_path.with_suffix(".png")
        out_path.write_bytes(png_bytes)
        return out_path


class ReplicateImageBackend(ImageBackend):
    def __init__(self, model: str = "black-forest-labs/flux-1.1-pro"):
        import replicate
        self._client = replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])
        self._model = model

    def generate(self, prompt: str, aspect: str, out_path: Path) -> Path:
        import httpx
        output = self._client.run(
            self._model,
            input={"prompt": prompt, "aspect_ratio": aspect, "output_format": "png"},
        )
        url = output[0] if isinstance(output, list) else output
        png_bytes = httpx.get(str(url), timeout=60).content
        out_path = out_path.with_suffix(".png")
        out_path.write_bytes(png_bytes)
        return out_path


class StubBackend(ImageBackend):
    """Writes a placeholder SVG that shows the prompt text. No API key required."""

    def generate(self, prompt: str, aspect: str, out_path: Path) -> Path:
        w, h = _ASPECT_TO_WH.get(aspect, (1024, 1024))
        # Wrap prompt text crudely for display.
        words = prompt.split()
        lines: list[str] = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 > 60:
                lines.append(current)
                current = word
            else:
                current = f"{current} {word}".strip()
        if current:
            lines.append(current)
        lines = lines[:14]

        tspans = "".join(
            f'<tspan x="50%" dy="{0 if i == 0 else 36}">{escape(line)}</tspan>'
            for i, line in enumerate(lines)
        )
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#1a1a2e"/>
      <stop offset="100%" stop-color="#4e1a4e"/>
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#g)"/>
  <text x="50%" y="40%" text-anchor="middle" fill="#f5c542" font-family="Georgia, serif" font-size="48" font-style="italic">[ placeholder ]</text>
  <text x="50%" y="50%" text-anchor="middle" fill="#fafafa" font-family="Helvetica, Arial, sans-serif" font-size="26">{tspans}</text>
</svg>"""
        out_path = out_path.with_suffix(".svg")
        out_path.write_text(svg, encoding="utf-8")
        return out_path


def build_backend(name: str | None = None) -> ImageBackend:
    name = (name or os.environ.get("ALFRED_IMAGE_BACKEND") or "openai").lower()
    if name == "openai":
        return OpenAIImageBackend()
    if name == "replicate":
        return ReplicateImageBackend()
    if name == "stub":
        return StubBackend()
    raise ValueError(f"Unknown ALFRED_IMAGE_BACKEND: {name!r}. Use openai | replicate | stub.")
