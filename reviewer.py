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
    improved = CVData.model_validate_json(
        chat_json(prompt, CVData.model_json_schema(), model))
    return enforce_facts(cv, improved)


def enforce_facts(original: CVData, improved: CVData) -> CVData:
    """Blokada faktów: poprawa może zmieniać opisy, ale nie twarde dane.

    Imię, kontakt, edukacja, nazwy firm, stanowiska i daty muszą pozostać
    jak w wersji pierwotnej. Doświadczenie wymyślone przez model (firma
    spoza oryginału) jest odrzucane, a brakujące przywracane.
    """
    improved.name = original.name
    improved.contact = original.contact
    improved.education = original.education

    improved_by_company = {e.company.strip().lower(): e
                           for e in improved.experience}
    merged = []
    for orig in original.experience:
        imp = improved_by_company.get(orig.company.strip().lower())
        if imp is not None:
            imp.company = orig.company
            imp.role = orig.role
            imp.dates = orig.dates
            merged.append(imp)
        else:
            merged.append(orig)
    improved.experience = merged
    return improved
