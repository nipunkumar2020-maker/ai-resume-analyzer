from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from extract_text import extract_text_from_pdf
from clean_text import clean_text

def match_score(resume_text, jd_text):
    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform([resume_text, jd_text])
    score = cosine_similarity(vectors[0], vectors[1])[0][0]
    return round(score * 100, 2)

if __name__ == "__main__":
    resume = clean_text(extract_text_from_pdf("sample_resume.pdf"))

    with open("job_description.txt", "r", encoding="utf-8") as f:
        jd = clean_text(f.read())

    print("Match Score:", match_score(resume, jd), "%")