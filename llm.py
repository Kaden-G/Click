"""Model adapter shared by serve.py and generate.py.

Reads click.config.json and sends one prompt to the configured endpoint.
Supported providers:
  openai     Any OpenAI-compatible /chat/completions endpoint (OpenAI, LiteLLM,
             vLLM, most enterprise AI gateways).
  azure      Azure OpenAI: base_url is the full deployment URL, including
             ?api-version=..., and the key goes in the api-key header.
  anthropic  Anthropic Messages API (/v1/messages).
Uses only the Python standard library.
"""
import json, os, pathlib, ssl, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).parent
CONFIG = ROOT / "click.config.json"


class LLMError(Exception):
    pass


def load_config():
    if not CONFIG.exists():
        raise LLMError("No click.config.json. Copy click.config.example.json to click.config.json and fill it in.")
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    for key in ("provider", "base_url", "model"):
        if not cfg.get(key):
            raise LLMError(f"click.config.json is missing '{key}'.")
    if cfg["provider"] not in ("openai", "azure", "anthropic"):
        raise LLMError("provider must be openai, azure or anthropic.")
    return cfg


def _key(cfg):
    env = cfg.get("api_key_env")
    if not env:
        return None
    val = os.environ.get(env)
    if not val:
        raise LLMError(f"Environment variable {env} is empty. Export your API key first.")
    return val


def complete(prompt, cfg, max_tokens=None, timeout=None):
    max_tokens = max_tokens or cfg.get("max_tokens", 4000)
    timeout = timeout or cfg.get("timeout_seconds", 180)
    key, p = _key(cfg), cfg["provider"]
    headers = {"Content-Type": "application/json"}
    msgs = [{"role": "user", "content": prompt}]
    if p == "anthropic":
        url = cfg["base_url"].rstrip("/") + "/v1/messages"
        body = {"model": cfg["model"], "max_tokens": max_tokens, "messages": msgs}
        headers["anthropic-version"] = cfg.get("anthropic_version", "2023-06-01")
        if key:
            headers["x-api-key"] = key
    else:
        url = cfg["base_url"] if p == "azure" else cfg["base_url"].rstrip("/") + "/chat/completions"
        body = {"messages": msgs, cfg.get("max_tokens_field", "max_tokens"): max_tokens}
        if p == "openai":
            body["model"] = cfg["model"]
        if key:
            headers["api-key" if p == "azure" else "Authorization"] = key if p == "azure" else "Bearer " + key
    if "temperature" in cfg:
        body["temperature"] = cfg["temperature"]
    headers.update(cfg.get("extra_headers", {}))
    ctx = ssl.create_default_context(cafile=cfg["ca_bundle"]) if cfg.get("ca_bundle") else None
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise LLMError(f"{e.code} from model endpoint: {e.read().decode('utf-8', 'replace')[:500]}")
    except (urllib.error.URLError, TimeoutError, ssl.SSLError) as e:
        raise LLMError(f"Couldn't reach the model endpoint: {e}")
    try:
        if p == "anthropic":
            return "".join(b.get("text", "") for b in data["content"] if b.get("type") == "text")
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise LLMError("Unexpected response shape: " + json.dumps(data)[:500])


def parse_json(text):
    """Read a JSON value from a model reply: whole text, a fenced block, or first bracket to last."""
    text = text.strip()
    try:
        return json.loads(text)
    except ValueError:
        pass
    if "```" in text:
        inner = text.split("```")[1]
        inner = inner[inner.find("\n") + 1:] if inner.lstrip().startswith(("json", "JSON")) else inner
        try:
            return json.loads(inner)
        except ValueError:
            pass
    starts = [i for i in (text.find("["), text.find("{")) if i >= 0]
    if starts:
        s = min(starts)
        e = max(text.rfind("]"), text.rfind("}"))
        try:
            return json.loads(text[s:e + 1])
        except ValueError:
            pass
    raise LLMError("The model's reply wasn't valid JSON.")
