from llm import chat_json
from loader import load_prompt_template
from models import CVData


def generate_cv(company: str, user: str, model: str = "qwen2.5:7b") -> CVData:
    prompt = load_prompt_template("prompts/cv_prompt.txt").format(
        company=company, user=user)
    return CVData.model_validate_json(
        chat_json(prompt, CVData.model_json_schema(), model))
