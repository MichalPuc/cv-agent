"""Renderer PDF (fpdf2) odwzorowujący dwukolumnowy szablon CV."""
from pathlib import Path

from fpdf import FPDF

from models import CVData

FONTS = Path(__file__).parent / "fonts"

# kolory
NAVY = (42, 58, 84)
DARK = (55, 65, 75)
GRAY = (90, 95, 100)
LINE_GRAY = (120, 120, 120)

# geometria (mm, A4 = 210 x 297)
MARGIN = 15
LEFT_X = MARGIN
LEFT_W = 55
TIMELINE_X = 81
RIGHT_X = 91
RIGHT_W = 195 - RIGHT_X
TOP = 20


class CVRenderer:
    def __init__(self, data: CVData):
        self.data = data
        pdf = FPDF(format="A4")
        pdf.set_auto_page_break(False)
        pdf.add_font("Lato", "", FONTS / "Lato-Regular.ttf")
        pdf.add_font("Lato", "B", FONTS / "Lato-Bold.ttf")
        pdf.add_font("LatoBlack", "", FONTS / "Lato-Black.ttf")
        pdf.add_font("LatoSemi", "", FONTS / "Lato-Semibold.ttf")
        pdf.add_page()
        self.pdf = pdf

    # ---------- pomocnicze ----------

    def _section_header(self, x, y, w, text, size=13):
        pdf = self.pdf
        pdf.set_xy(x, y)
        pdf.set_font("LatoBlack", "", size)
        pdf.set_text_color(*NAVY)
        pdf.set_char_spacing(0.9)
        pdf.cell(w, 6, text.upper())
        pdf.set_char_spacing(0)
        pdf.set_draw_color(*NAVY)
        pdf.set_line_width(0.5)
        pdf.line(x, y + 8.5, x + w, y + 8.5)
        return y + 12.5

    def _timeline_badge(self, cy, kind):
        """Granatowe kółko z białą ikoną na osi czasu."""
        pdf = self.pdf
        cx, r = TIMELINE_X, 4.0
        pdf.set_fill_color(*NAVY)
        pdf.ellipse(cx - r, cy - r, 2 * r, 2 * r, "F")
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(255, 255, 255)
        if kind == "person":
            pdf.ellipse(cx - 1.1, cy - 2.5, 2.2, 2.2, "F")   # głowa
            pdf.ellipse(cx - 2.0, cy + 0.1, 4.0, 3.4, "F")    # ramiona
            pdf.set_fill_color(*NAVY)
            pdf.rect(cx - 2.6, cy + 2.0, 5.2, 2.4, "F")       # przycięcie
        elif kind == "case":
            pdf.set_line_width(0.5)
            pdf.rect(cx - 1.0, cy - 2.1, 2.0, 1.2)            # rączka
            pdf.rect(cx - 2.1, cy - 1.3, 4.2, 3.2, "F")       # walizka
            pdf.set_draw_color(*NAVY)
            pdf.set_line_width(0.35)
            pdf.line(cx - 2.1, cy + 0.3, cx + 2.1, cy + 0.3)
        elif kind == "cap":
            pdf.polygon(
                [(cx, cy - 2.3), (cx + 2.9, cy - 0.9),
                 (cx, cy + 0.5), (cx - 2.9, cy - 0.9)], "F")  # biret
            pdf.polygon(
                [(cx - 1.5, cy + 0.2), (cx + 1.5, cy + 0.2),
                 (cx + 1.5, cy + 1.8), (cx - 1.5, cy + 1.8)], "F")
            pdf.set_line_width(0.3)
            pdf.line(cx + 2.9, cy - 0.9, cx + 2.9, cy + 1.6)  # frędzel

    def _timeline_dot(self, cy):
        pdf = self.pdf
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(*LINE_GRAY)
        pdf.set_line_width(0.3)
        r = 1.2
        pdf.ellipse(TIMELINE_X - r, cy - r, 2 * r, 2 * r, "FD")

    def _contact_icon(self, x, cy, kind):
        pdf = self.pdf
        pdf.set_draw_color(*NAVY)
        pdf.set_fill_color(*NAVY)
        if kind == "phone":
            pdf.set_line_width(0.7)
            # słuchawka: łuk z dwoma zgrubieniami
            pdf.ellipse(x, cy - 1.0, 1.4, 1.4, "F")
            pdf.ellipse(x + 2.2, cy + 1.2, 1.4, 1.4, "F")
            pdf.set_line_width(0.55)
            pdf.line(x + 0.9, cy + 0.2, x + 2.7, cy + 2.0)
        elif kind == "mail":
            pdf.set_line_width(0.4)
            pdf.rect(x, cy - 1.2, 3.8, 2.8, "F")
            pdf.set_draw_color(255, 255, 255)
            pdf.set_line_width(0.35)
            pdf.line(x + 0.3, cy - 0.9, x + 1.9, cy + 0.4)
            pdf.line(x + 3.5, cy - 0.9, x + 1.9, cy + 0.4)
        elif kind == "web":
            pdf.set_line_width(0.35)
            pdf.ellipse(x, cy - 1.6, 3.6, 3.6)          # glob
            pdf.ellipse(x + 1.1, cy - 1.6, 1.4, 3.6)    # południk
            pdf.line(x, cy + 0.2, x + 3.6, cy + 0.2)    # równik

    def _bullet_list(self, x, w, items, size=10, lh=5.6, gap=1.4):
        pdf = self.pdf
        pdf.set_font("Lato", "", size)
        pdf.set_text_color(*DARK)
        for item in items:
            y = pdf.get_y()
            pdf.set_xy(x + 1, y)
            pdf.cell(3, lh, "•")
            pdf.set_xy(x + 4.5, y)
            pdf.multi_cell(w - 4.5, lh, item, align="L")
            pdf.set_y(pdf.get_y() + gap)

    # ---------- sekcje ----------

    def _header(self):
        pdf, d = self.pdf, self.data
        pdf.set_xy(MARGIN, TOP)
        pdf.set_font("LatoBlack", "", 27)
        pdf.set_text_color(*NAVY)
        pdf.set_char_spacing(0.6)
        pdf.cell(0, 11, d.name.upper())
        pdf.set_xy(MARGIN, TOP + 12)
        pdf.set_font("Lato", "", 13)
        pdf.set_text_color(*DARK)
        pdf.set_char_spacing(0.8)
        pdf.cell(0, 7, d.title.upper())
        pdf.set_char_spacing(0)
        pdf.set_draw_color(*NAVY)
        pdf.set_line_width(1.1)
        pdf.line(MARGIN, TOP + 23, 195, TOP + 23)

    def _left_column(self, y):
        pdf, d = self.pdf, self.data
        # CONTACT
        y = self._section_header(LEFT_X, y, LEFT_W - 8, "Contact")
        pdf.set_font("Lato", "", 9)
        items = [
            ("phone", d.contact.phone),
            ("mail", d.contact.email),
            ("web", d.contact.linkedin),
        ]
        for kind, text in items:
            if not text:
                continue
            self._contact_icon(LEFT_X + 1, y + 2.0, kind)
            pdf.set_xy(LEFT_X + 7, y)
            pdf.set_font("Lato", "", 9)
            pdf.set_text_color(*DARK)
            if kind == "web":
                pdf.set_font("Lato", "U", 9)
                pdf.multi_cell(LEFT_W - 7, 4.8, text, align="L",
                               link=text if text.startswith("http") else "")
            else:
                pdf.multi_cell(LEFT_W - 7, 4.8, text, align="L")
            y = pdf.get_y() + 2.2
        # SKILLS
        y = self._section_header(LEFT_X, y + 6, LEFT_W - 8, "Skills")
        pdf.set_y(y + 1)
        self._bullet_list(LEFT_X, LEFT_W, d.skills, size=10, lh=5.4, gap=1.2)
        # LANGUAGES
        y = self._section_header(LEFT_X, pdf.get_y() + 6, LEFT_W - 8, "Languages")
        pdf.set_y(y + 1)
        self._bullet_list(LEFT_X, LEFT_W, d.languages, size=10, lh=5.4, gap=1.2)

    def _right_column(self, y):
        pdf, d = self.pdf, self.data
        # oś czasu
        pdf.set_draw_color(*LINE_GRAY)
        pdf.set_line_width(0.3)
        pdf.line(TIMELINE_X, y + 3, TIMELINE_X, 272)

        # PROFILE
        self._timeline_badge(y + 3.5, "person")
        y = self._section_header(RIGHT_X, y, RIGHT_W, "Profile", size=14)
        pdf.set_xy(RIGHT_X, y)
        pdf.set_font("Lato", "", 9.5)
        pdf.set_text_color(*DARK)
        pdf.multi_cell(RIGHT_W, 5.0, d.profile, align="J")
        y = pdf.get_y() + 7

        # WORK EXPERIENCE
        self._timeline_badge(y + 3.5, "case")
        y = self._section_header(RIGHT_X, y, RIGHT_W, "Work Experience", size=14)
        pdf.set_y(y)
        for job in d.experience:
            jy = pdf.get_y()
            self._timeline_dot(jy + 2.8)
            pdf.set_xy(RIGHT_X, jy)
            pdf.set_font("Lato", "B", 11)
            pdf.set_text_color(*NAVY)
            pdf.cell(RIGHT_W - 32, 5.6, job.company)
            pdf.set_font("Lato", "", 9.5)
            pdf.set_text_color(*DARK)
            pdf.cell(32, 5.6, job.dates, align="R")
            pdf.set_xy(RIGHT_X, jy + 5.6)
            pdf.set_font("Lato", "", 10.5)
            pdf.cell(RIGHT_W, 5.4, job.role)
            pdf.set_y(jy + 11.6)
            self._bullet_list(RIGHT_X + 1, RIGHT_W - 1, job.bullets,
                              size=9.5, lh=4.9, gap=0.6)
            pdf.set_y(pdf.get_y() + 4)

        # EDUCATION
        y = pdf.get_y() + 2
        self._timeline_badge(y + 3.5, "cap")
        y = self._section_header(RIGHT_X, y, RIGHT_W, "Education", size=14)
        pdf.set_y(y + 1)
        for edu in d.education:
            ey = pdf.get_y()
            self._timeline_dot(ey + 2.8)
            pdf.set_xy(RIGHT_X, ey)
            pdf.set_font("Lato", "B", 11)
            pdf.set_text_color(*NAVY)
            pdf.cell(RIGHT_W - 32, 5.6, edu.degree)
            pdf.set_font("Lato", "", 9.5)
            pdf.set_text_color(*DARK)
            pdf.cell(32, 5.6, edu.dates, align="R")
            pdf.set_xy(RIGHT_X, ey + 5.6)
            pdf.set_font("Lato", "", 10.5)
            pdf.cell(RIGHT_W, 5.4, edu.school)
            pdf.set_y(ey + 13)

    # ---------- API ----------

    def render(self, path: str | Path):
        self._header()
        body_y = TOP + 32
        self._right_column(body_y)
        self._left_column(body_y)
        self.pdf.output(str(path))


def render_cv(data: CVData, path: str | Path):
    CVRenderer(data).render(path)
