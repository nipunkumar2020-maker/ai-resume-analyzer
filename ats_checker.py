import re

SECTION_PATTERNS = {
    "Education": r"^\s*(education|academic)",
    "Experience": r"^\s*(experience|work history|employment|internship)",
    "Skills": r"^\s*(technical skills|skills|core competencies)",
    "Projects": r"^\s*(projects|project work)",
}

def has_email(text):
    return re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text) is not None

def has_phone(text):
    for m in re.finditer(r"\+?\d[\d\s\-()]{8,}\d", text):
        digits = re.sub(r"\D", "", m.group())
        if 10 <= len(digits) <= 13:
            return True
    return False

def find_sections(raw_text):
    lowered = raw_text.lower()
    found = {}
    for name, pattern in SECTION_PATTERNS.items():
        found[name] = re.search(pattern, lowered, re.MULTILINE) is not None
    return found

def count_numbers(text):
    pattern = r"\d+(?:\.\d+)?\s*%|\d[\d,]*\+|\b\d{1,3}(?:,\d{3})+\b"
    return len(re.findall(pattern, text))

def check_ats(raw_text, skill_score):
    checks = []

    def add(label, earned, maximum, message):
        checks.append({"label": label, "earned": earned, "max": maximum,
                       "passed": earned == maximum, "message": message})

    # 1. Email (10)
    ok = has_email(raw_text)
    add("Email address", 10 if ok else 0, 10,
        "Email found." if ok else "No email found. Add a professional email address.")

    # 2. Phone (10)
    ok = has_phone(raw_text)
    add("Phone number", 10 if ok else 0, 10,
        "Phone number found." if ok else "No phone number found. Add one in the header.")

    # 3. Sections (4 x 8 = 32)
    sections = find_sections(raw_text)
    for name, present in sections.items():
        add(f"{name} section", 8 if present else 0, 8,
            f"'{name}' heading found." if present
            else f"No clear '{name}' heading. Use a standard heading so ATS can find it.")

    # 4. Length (10)
    words = len(raw_text.split())
    if 250 <= words <= 800:
        add("Resume length", 10, 10, f"{words} words. Good length (about 1-2 pages).")
    else:
        add("Resume length", 5, 10,
            f"{words} words. Aim for roughly 250-800 words (1-2 pages).")

    # 5. Quantified achievements (15)
    nums = count_numbers(raw_text)
    if nums >= 3:
        add("Quantified achievements", 15, 15, f"{nums} measurable results found (percentages, counts).")
    elif nums >= 1:
        add("Quantified achievements", 8, 15,
            f"Only {nums} measurable result found. Add more numbers (%, counts, time saved).")
    else:
        add("Quantified achievements", 0, 15,
            "No measurable results found. Add numbers to show your impact.")

    # 6. Parsing problems (8)
    if "(cid:" in raw_text:
        add("Readable characters", 0, 8,
            "Some symbols (like bullets) could not be read as text. "
            "This can happen with custom fonts and may confuse some ATS.")
    else:
        add("Readable characters", 8, 8, "All characters were extracted cleanly.")

    # 7. Keyword coverage (15)
    earned = round(skill_score / 100 * 15)
    add("Job keyword coverage", earned, 15,
        f"Your resume covers {skill_score}% of the skills in the job description.")

    total = sum(c["earned"] for c in checks)
    return {"score": total, "checks": checks}

if __name__ == "__main__":
    from extract_text import extract_text_from_pdf
    from clean_text import clean_text
    from analyzer import analyze

    raw = extract_text_from_pdf("sample_resume.pdf")
    with open("job_description.txt", "r", encoding="utf-8") as f:
        jd = f.read()
    skill_score = analyze(clean_text(raw), clean_text(jd))["skill_score"]

    result = check_ats(raw, skill_score)
    print("ATS Friendliness Score:", result["score"], "/ 100\n")
    for c in result["checks"]:
        mark = "PASS" if c["passed"] else "FAIL"
        print(f"[{mark}] {c['label']} ({c['earned']}/{c['max']}): {c['message']}")