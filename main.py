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
                   help="model Ollama")
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

        for i in range(1, args.review + 1):
            print(f"Recenzuję (iteracja {i}/{args.review})...")
            review = review_cv(company, user, data, args.model)
            print_review(i, review)
            if review.match_score >= SCORE_TARGET:
                print(f"Wynik >= {SCORE_TARGET}, kończę poprawki.")
                break
            print("Poprawiam CV zgodnie z recenzją...")
            data = improve_cv(company, user, data, review, args.model)

        json_path = out.with_suffix(".json")
        json_path.write_text(data.model_dump_json(indent=2), encoding="utf-8")
        print(f"\nZapisano dane: {json_path}")

    render_cv(data, out)
    print(f"Zapisano CV: {out}")


if __name__ == "__main__":
    main()
