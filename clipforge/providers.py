"""Provider adapters: one interface, swappable backends.

ClipForge never depends on a single LLM vendor (master-prompt rule). This
module adapts:
  - "zai":    the z-ai CLI available in this runtime (cloud, key handled
              outside the repo by the CLI itself)
  - "ollama": a local Ollama server (key-free, local-first default)
  - "none":   no provider (heuristic-only operation; translation disabled)

Selection: get_provider() explicit arg > CLIPFORGE_PROVIDER env > "ollama"
when reachable > "zai" when the CLI exists > None.
"""
import json
import os
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request


class ZaiCLIProvider:
    """z-ai CLI chat adapter (used in this sandbox; output JSON parsed
    defensively because the exact response schema is CLI-defined)."""

    name = "zai"

    def __init__(self, bin_path="z-ai", timeout=120):
        self.bin = shutil.which(bin_path) or bin_path
        self.timeout = timeout

    def available(self):
        try:
            return subprocess.run([self.bin, "--help"],
                                  capture_output=True).returncode == 0
        except OSError:
            return False

    def complete(self, prompt, system=None, temperature=None):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            out_path = tf.name
        cmd = [self.bin, "chat", "-p", prompt, "-o", out_path]
        if system:
            cmd += ["-s", system]
        try:
            proc = subprocess.run(cmd, capture_output=True,
                                  timeout=self.timeout)
            if proc.returncode != 0:
                raise RuntimeError(
                    f"z-ai chat failed: {proc.stderr.decode()[-300:]}")
            with open(out_path) as f:
                data = json.load(f)
        finally:
            try:
                os.unlink(out_path)
            except OSError:
                pass
        # defensive extraction across possible shapes
        if isinstance(data, dict):
            for key in ("content", "output", "text", "response"):
                if isinstance(data.get(key), str) and data[key].strip():
                    return data[key]
            msg = data.get("message")
            if isinstance(msg, dict) and isinstance(msg.get("content"), str):
                return msg["content"]
            choices = data.get("choices")
            if isinstance(choices, list) and choices:
                c0 = choices[0]
                m = c0.get("message") if isinstance(c0, dict) else None
                if isinstance(m, dict) and isinstance(m.get("content"), str):
                    return m["content"]
        raise RuntimeError(f"z-ai chat: unrecognized output shape: "
                           f"{list(data) if isinstance(data, dict) else type(data)}")


class OllamaProvider:
    name = "ollama"

    def __init__(self, model="qwen2.5:3b", url="http://localhost:11434",
                 timeout=600):
        self.model, self.url, self.timeout = model, url, timeout

    def available(self):
        try:
            with urllib.request.urlopen(f"{self.url}/api/tags", timeout=3) \
                    as r:
                return r.status == 200
        except (OSError, urllib.error.URLError):
            return False

    def complete(self, prompt, system=None, temperature=0.3):
        body = {"model": self.model, "stream": False,
                "messages": ([{"role": "system", "content": system}]
                             if system else []) +
                            [{"role": "user", "content": prompt}],
                "options": {"temperature": temperature}}
        req = urllib.request.Request(
            f"{self.url}/api/chat",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.load(r)["message"]["content"]


PROVIDERS = {"zai": ZaiCLIProvider, "ollama": OllamaProvider}


def get_provider(preferred=None):
    """Return an available provider or None. Never raises."""
    order = ([preferred] if preferred else
             [os.environ.get("CLIPFORGE_PROVIDER")] if
             os.environ.get("CLIPFORGE_PROVIDER") else
             ["ollama", "zai"])
    for name in filter(None, order):
        cls = PROVIDERS.get(name)
        if cls and cls().available():
            return cls()
    return None


def extract_json(text):
    """Parse the first JSON object/array from an LLM reply (tolerates code
    fences and prose around it). Raises ValueError when nothing parses."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text,
                  flags=re.MULTILINE).strip() if text.startswith("```") \
        else text
    start = min([i for i in (text.find("{"), text.find("[")) if i >= 0],
                default=-1)
    if start < 0:
        raise ValueError("no JSON found in reply")
    opener = text[start]
    closer = {"{": "}", "[": "]"}[opener]
    depth = 0
    for i in range(start, len(text)):
        if text[i] == opener:
            depth += 1
        elif text[i] == closer:
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i + 1])
    raise ValueError("unterminated JSON in reply")


import re  # noqa: E402  (kept at bottom to keep the adapter block readable)
