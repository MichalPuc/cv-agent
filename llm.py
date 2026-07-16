"""Wspólna warstwa komunikacji z Ollama (structured outputs)."""


def chat_json(prompt: str, schema: dict, model: str) -> str:
    import ollama  # lazy import: render z JSON-a nie wymaga Ollamy

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        format=schema,
        options={"temperature": 0.2},
    )
    return response["message"]["content"]
