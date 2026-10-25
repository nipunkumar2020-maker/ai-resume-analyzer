import os
from openai import OpenAI

MODEL = "recursive/flint-v1.0:free"  # check openrouter.ai/models for a currently available free model

def ask_llm(prompt, max_tokens=None):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set.")

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    kwargs = {"model": MODEL, "messages": [{"role": "user", "content": prompt}]}
    if max_tokens:
        kwargs["max_tokens"] = max_tokens
    response = client.chat.completions.create(**kwargs)

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("The model returned an empty response.")
    return content

def get_ai_feedback(resume_text, jd_text, missing_skills):
    prompt = f"""You are an experienced technical recruiter reviewing a resume against a job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

Skills the job asks for that were not found in the resume: {", ".join(missing_skills) or "none"}

Give feedback in exactly these four sections, using short bullet points:

## Summary Review
Is the professional summary strong and relevant to this job? What should change?

## Strengths
The 3 strongest points of this resume for this job.

## Weaknesses
The 3 biggest weaknesses or gaps for this job.

## Bullet Point Improvements
Pick 2 weak bullet points from the resume and rewrite them to be stronger.
Do NOT invent experience, tools, or numbers that are not in the resume.
"""
    return ask_llm(prompt)

if __name__ == "__main__":
    from extract_text import extract_text_from_pdf
    from clean_text import clean_text
    from analyzer import analyze

    raw = extract_text_from_pdf("sample_resume.pdf")
    with open("job_description.txt", "r", encoding="utf-8") as f:
        jd_raw = f.read()

    result = analyze(clean_text(raw), clean_text(jd_raw))
    print(get_ai_feedback(raw, jd_raw, result["missing"]))