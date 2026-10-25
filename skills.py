import re
from extract_text import extract_text_from_pdf
from clean_text import clean_text

SKILLS = {
    "Languages": ["python", "sql", "r", "java", "c++", "c#", "javascript", "scala"],
    "Libraries": ["pandas", "numpy", "scikit-learn", "matplotlib", "seaborn",
                  "tensorflow", "keras", "pytorch", "nltk", "spacy", "opencv"],
    "ML / AI": ["machine learning", "deep learning", "nlp", "computer vision",
                "linear regression", "logistic regression", "random forest",
                "xgboost", "k-means", "neural network", "feature engineering",
                "tf-idf", "time series"],
    "Tools": ["jupyter notebook", "git", "github", "power bi", "tableau",
              "excel", "streamlit", "mysql", "mongodb", "docker", "aws",
              "spark", "hadoop", "flask"],
}

def find_skills(cleaned_text):
    found = {}
    for category, skill_list in SKILLS.items():
        matched = []
        for skill in skill_list:
            pattern = r"(?<![a-z0-9+#\-])" + re.escape(skill) + r"(?![a-z0-9+#\-])"
            if re.search(pattern, cleaned_text):
                matched.append(skill)
        if matched:
            found[category] = matched
    return found

if __name__ == "__main__":
    raw = extract_text_from_pdf("sample_resume.pdf")
    cleaned = clean_text(raw)
    result = find_skills(cleaned)

    total = 0
    for category, skills in result.items():
        print(f"{category}: {', '.join(skills)}")
        total += len(skills)
    print("\nTotal skills found:", total)