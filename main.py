import argparse
from pathlib import Path

from generator import generate_cv
from loader import read_file
from models import CVData
from renderer import render_cv
from reviewer import improve_cv, review_cv

SCORE_TARGET = 90


def parse_args():
    p = argparse.ArgumentParser(description="Generator CV dopasowanego do firmy")
    p.add_argument("-c", "--company", default="documents/company_requirements.txt",
                   help="plik z wymaganiami firmy")
    p.add_argument("-u", "--user", default="documents/user_profile.txt",
                   help="plik z profilem kandydata")
    p.add_argument("-m", "--model", default="qwen2.5:7b",
                   help="model Ollama do generacji")
    p.add_argument("--review-model", default=None, metavar="MODEL",
                   help="model Ollama do recenzji (domyślnie ten sam co -m)")
    p.add_argument("-o", "--output", default="output/cv.pdf",
                   help="ścieżka wyjściowego PDF")
    p.add_argument("-r", "--review", type=int, default=1, metavar="N",
                   help="liczba iteracji recenzji i poprawy (0 = wyłącz)")
    p.add_argument("--from-json", metavar="PLIK",
                   help="pomiń LLM, renderuj z gotowego JSON-a")
    return p.parse_args()


def print_review(i, review):
    print(f"\nRecenzja {i}: dopasowanie {review.match_score}/100")
    if review.missing_keywords:
        print("  Brakujące słowa kluczowe:", ", ".join(review.missing_keywords))
    for w in review.weak_points:
        print(f"  Słaby punkt: {w}")
    for s in review.suggestions:
        print(f"  Sugestia: {s}")


def review_loop(data, company, user, iterations, model):
    """Pętla recenzja -> poprawa. Zwraca najlepiej ocenioną wersję CV."""
    best_data, best_score = data, -1
    history = []
    improved_since_review = False

    for i in range(1, iterations + 1):
        print(f"Recenzuję (iteracja {i}/{iterations})...")
        review = review_cv(company, user, data, model)
        history.append(review)
        improved_since_review = False
        print_review(i, review)
        if review.match_score > best_score:
            best_data, best_score = data, review.match_score
        if review.match_score >= SCORE_TARGET:
            print(f"Wynik >= {SCORE_TARGET}, kończę poprawki.")
            break
        print("Poprawiam CV zgodnie z recenzją...")
        data = improve_cv(company, user, data, review, model)
        improved_since_review = True

    if improved_since_review:
        print("Recenzja końcowa poprawionej wersji...")
        review = review_cv(company, user, data, model)
        history.append(review)
        print_review(len(history), review)
        if review.match_score > best_score:
            best_data, best_score = data, review.match_score

    print(f"\nWybieram wersję z wynikiem {best_score}/100.")
    return best_data, best_score, history


def save_report(path, history, final_score):
    lines = [f"# Raport recenzji CV\n\nWynik końcowy: **{final_score}/100**\n"]
    for i, r in enumerate(history, 1):
        lines.append(f"\n## Iteracja {i} — {r.match_score}/100\n")
        if r.missing_keywords:
            lines.append("Brakujące słowa kluczowe: "
                         + ", ".join(r.missing_keywords) + "\n")
        lines += [f"- Słaby punkt: {w}\n" for w in r.weak_points]
        lines += [f"- Sugestia: {s}\n" for s in r.suggestions]
    path.write_text("".join(lines), encoding="utf-8")
    print(f"Zapisano raport recenzji: {path}")


def main():
    args = parse_args()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.from_json:
        data = CVData.model_validate_json(read_file(args.from_json))
    else:
        company = read_file(args.company)
        user = read_file(args.user)
        print(f"Generuję CV modelem {args.model}...")
        data = generate_cv(company, user, args.model)

        if args.review > 0:
            review_model = args.review_model or args.model
            data, score, history = review_loop(
                data, company, user, args.review, review_model)
            save_report(out.with_name(out.stem + "_review.md"), history, score)

        json_path = out.with_suffix(".json")
        json_path.write_text(data.model_dump_json(indent=2), encoding="utf-8")
        print(f"Zapisano dane: {json_path}")

    render_cv(data, out)
    print(f"Zapisano CV: {out}")


if __name__ == "__main__":
    main()
