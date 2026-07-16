from pydantic import BaseModel, Field


class Contact(BaseModel):
    phone: str = ""
    email: str = ""
    linkedin: str = ""


class Experience(BaseModel):
    company: str
    role: str
    dates: str = Field(description="np. 08/2024 - PRESENT")
    bullets: list[str] = Field(description="Punkty opisujące zakres obowiązków")


class Education(BaseModel):
    degree: str
    school: str
    dates: str = ""


class Review(BaseModel):
    match_score: int = Field(
        ge=0, le=100,
        description="Dopasowanie CV do oferty w skali 0-100")
    missing_keywords: list[str] = Field(
        description="Istotne słowa kluczowe z oferty nieobecne w CV, "
                    "które mają pokrycie w profilu kandydata")
    weak_points: list[str] = Field(
        description="Słabe lub zbyt ogólne fragmenty CV")
    suggestions: list[str] = Field(
        description="Konkretne poprawki do wprowadzenia, "
                    "oparte wyłącznie na danych z profilu kandydata")


class CVData(BaseModel):
    name: str
    title: str = Field(description="Stanowisko, np. JAVA SOFTWARE ENGINEER")
    contact: Contact
    skills: list[str]
    languages: list[str] = Field(description='np. ["English C1", "Polish Native"]')
    profile: str = Field(description="Podsumowanie zawodowe, 4-6 zdań")
    experience: list[Experience]
    education: list[Education]
