import json

def try_parse_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None

def extract_first_code_block(text: str):
    if "```" not in text:
        return text
    parts = text.split("```")
    # first code block is parts[1] if parts length > 1
    if len(parts) >= 2:
        candidate = parts[1]
        if candidate.strip().startswith("python"):
            candidate = candidate.split("\n", 1)[1] if "\n" in candidate else ""
        return candidate
    return text
