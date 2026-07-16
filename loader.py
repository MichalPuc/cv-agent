from pathlib import Path


def read_file(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_prompt_template(path: str | Path = "prompts/cv_prompt.txt") -> str:
    return read_file(Path(__file__).parent / path)
