from llm import chat_json
from loader import load_prompt_template
from models import CVData, Review


def review_cv(company: str, user: str, cv: CVData,
              model: str = "qwen2.5:7b") -> Review:
    prompt = load_prompt_template("prompts/review_prompt.txt").format(
        company=company, user=user, cv=cv.model_dump_json(indent=2))
    return Review.model_validate_json(
        chat_json(prompt, Review.model_json_schema(), model))


def improve_cv(company: str, user: str, cv: CVData, review: Review,
               model: str = "qwen2.5:7b") -> CVData:
    prompt = load_prompt_template("prompts/improve_prompt.txt").format(
        company=company, user=user,
        cv=cv.model_dump_json(indent=2),
        review=review.model_dump_json(indent=2))
    return CVData.model_validate_json(
        chat_json(prompt, CVData.model_json_schema(), model))
