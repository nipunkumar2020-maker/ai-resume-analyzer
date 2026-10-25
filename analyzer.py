from extract_text import extract_text_from_pdf
from clean_text import clean_text
from skills import find_skills
from matcher import match_score

def skills_as_set(found_dict):
    all_skills = set()
    for skill_list in found_dict.values():
        all_skills.update(skill_list)
    return all_skills

def analyze(resume_text, jd_text):
    resume_skills = skills_as_set(find_skills(resume_text))
    jd_skills = skills_as_set(find_skills(jd_text))

    matched = resume_skills & jd_skills
    missing = jd_skills - resume_skills
    extra = resume_skills - jd_skills

    if jd_skills:
        skill_score = round(len(matched) / len(jd_skills) * 100, 2)
    else:
        skill_score = 0

    return {
        "text_score": match_score(resume_text, jd_text),
        "skill_score": skill_score,
        "matched": sorted(matched),
        "missing": sorted(missing),
        "extra": sorted(extra),
    }

if __name__ == "__main__":
    resume = clean_text(extract_text_from_pdf("sample_resume.pdf"))
    with open("job_description.txt", "r", encoding="utf-8") as f:
        jd = clean_text(f.read())

    r = analyze(resume, jd)

    print("Text Match Score :", r["text_score"], "%")
    print("Skill Match Score:", r["skill_score"], "%")
    print()
    print("Matched skills :", ", ".join(r["matched"]))
    print("Missing skills :", ", ".join(r["missing"]))
    print("Extra skills   :", ", ".join(r["extra"]))
    print()
    print("Suggestions:")
    for skill in r["missing"]:
        print(f"- Add '{skill}' to your resume if you have experience with it.")