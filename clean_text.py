import re
from extract_text import extract_text_from_pdf

def clean_text(text):
    # 1. PDF ke ajeeb bullet codes hatao, jaise (cid:127)
    text = re.sub(r"\(cid:\d+\)", " ", text)

    # 2. Sab kuch lowercase karo
    text = text.lower()

    # 3. Kaam ke characters rakho, baaki ko space bana do
    text = re.sub(r"[^a-z0-9+#.\-\s]", " ", text)

    # 4. Ek se zyada spaces/newlines ko ek space bana do
    text = re.sub(r"\s+", " ", text)

    return text.strip()

if __name__ == "__main__":
    raw = extract_text_from_pdf("sample_resume.pdf")
    cleaned = clean_text(raw)

    print("RAW length    :", len(raw))
    print("CLEANED length:", len(cleaned))
    print()
    print(cleaned)