import io

import streamlit as st
from extract_text import extract_text_from_pdf
from clean_text import clean_text
from analyzer import analyze
from ai_feedback import get_ai_feedback
from ats_checker import check_ats
from ui_helpers import CSS, score_card, chips, check_row
from resume_builder import rewrite_resume, build_pdf

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

# ---------- Header ----------
st.markdown(
    '<div class="hero"><h1>📄 AI Resume Analyzer</h1>'
    '<p>Check how well your resume matches a job, find missing skills, and get AI feedback.</p></div>',
    unsafe_allow_html=True,
)

# ---------- Sidebar (inputs) ----------
with st.sidebar:
    st.header("Your inputs")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    jd_input = st.text_area("Paste the job description", height=260)
    analyze_clicked = st.button("Analyze Resume", type="primary")
    st.caption("Note: your resume text is sent to an AI model to generate feedback.")

# ---------- Run analysis and save it ----------
if analyze_clicked:
    if uploaded_file is None or not jd_input.strip():
        st.warning("Please upload a resume and paste a job description first.")
    else:
        raw_text = extract_text_from_pdf(uploaded_file)
        if not raw_text.strip():
            st.error("No text could be extracted from this PDF. It may be a scanned image.")
        else:
            result = analyze(clean_text(raw_text), clean_text(jd_input))
            ats = check_ats(raw_text, result["skill_score"])

            feedback, feedback_error = None, None
            try:
                with st.spinner("Reviewing your resume..."):
                    feedback = get_ai_feedback(raw_text, jd_input, result["missing"])
            except Exception as e:
                feedback_error = str(e)

            st.session_state["analysis"] = {
                "raw_text": raw_text,
                "jd_text": jd_input,
                "result": result,
                "ats": ats,
                "feedback": feedback,
                "feedback_error": feedback_error,
            }

# ---------- Show results ----------
data = st.session_state.get("analysis")

if data is None:
    st.info(
        "**How it works**\n\n"
        "1. Upload your resume (PDF) in the sidebar.\n"
        "2. Paste the job description.\n"
        "3. Click **Analyze Resume**."
    )
else:
    result, ats = data["result"], data["ats"]
    total_required = len(result["matched"]) + len(result["missing"])

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📊 Overview", "🧩 Skills", "🛡️ ATS Check", "🤖 AI Feedback", "✨ Improved Resume"]
    )

    with tab1:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(score_card("Skill Match", result["skill_score"], "%",
                        f"{len(result['matched'])} of {total_required} required skills"),
                        unsafe_allow_html=True)
        with c2:
            st.markdown(score_card("Text Match", result["text_score"], "%",
                        "Overall word similarity"), unsafe_allow_html=True)
        with c3:
            st.markdown(score_card("ATS Friendliness", ats["score"], "/100",
                        "Estimate only"), unsafe_allow_html=True)

        st.markdown("#### Missing skills")
        st.markdown(chips(result["missing"], "red", "None, great!"), unsafe_allow_html=True)

    with tab2:
        st.markdown("#### ✅ Matched skills")
        st.markdown(chips(result["matched"], "green"), unsafe_allow_html=True)
        st.markdown("#### ❌ Missing skills")
        st.markdown(chips(result["missing"], "red", "None, great!"), unsafe_allow_html=True)
        st.markdown("#### ➕ Extra skills (not asked for in the job)")
        st.markdown(chips(result["extra"], "blue"), unsafe_allow_html=True)

        if result["missing"]:
            st.markdown("#### Suggestions")
            for skill in result["missing"]:
                st.write(f"- If you have experience with **{skill}**, consider adding it to your resume.")

    with tab3:
        st.markdown(score_card("ATS Friendliness Score (estimate)", ats["score"], "/100",
                    "Every company's ATS works differently"), unsafe_allow_html=True)
        st.write("")
        for c in ats["checks"]:
            st.markdown(check_row(c["label"], c["earned"], c["max"], c["message"], c["passed"]),
                        unsafe_allow_html=True)

    with tab4:
        if data["feedback"]:
            st.markdown(data["feedback"])
        else:
            st.warning("AI feedback is unavailable right now. Check your API key and internet connection.")
            st.caption(f"Details: {data['feedback_error']}")

    with tab5:
        st.markdown("#### Generate an improved resume")
        st.write(
            "The AI will rewrite your resume to fit this job: a stronger summary, better bullet points "
            "and an ATS-friendly layout. It will **not** invent experience."
        )
        selected = st.multiselect(
            "Missing skills that you genuinely have (they will be added to your skills section)",
            options=result["missing"],
        )
        st.caption("Only select skills you can honestly talk about in an interview.")

        if st.button("Generate improved resume"):
            data.pop("improved", None)
            data.pop("improved_error", None)
            try:
                with st.spinner("Rewriting your resume..."):
                    new_data = rewrite_resume(data["raw_text"], data["jd_text"], selected)
                    pdf_bytes = build_pdf(new_data)
                new_raw = extract_text_from_pdf(io.BytesIO(pdf_bytes))
                new_result = analyze(clean_text(new_raw), clean_text(data["jd_text"]))
                new_ats = check_ats(new_raw, new_result["skill_score"])
                data["improved"] = {"pdf": pdf_bytes, "result": new_result, "ats": new_ats}
            except Exception as e:
                data["improved_error"] = str(e)

        if data.get("improved_error"):
            st.warning("Could not generate the improved resume. Please try again.")
            st.caption(f"Details: {data['improved_error']}")

        improved = data.get("improved")
        if improved:
            new_result, new_ats = improved["result"], improved["ats"]
            m1, m2 = st.columns(2)
            m1.metric("Skill Match", f"{new_result['skill_score']}%",
                      delta=f"{round(new_result['skill_score'] - result['skill_score'], 2)}%")
            m2.metric("ATS Friendliness", f"{new_ats['score']}/100",
                      delta=new_ats["score"] - ats["score"])

            st.download_button(
                "⬇️ Download improved resume (PDF)",
                data=improved["pdf"],
                file_name="improved_resume.pdf",
                mime="application/pdf",
            )
            st.warning(
                "AI can make mistakes. Read the new resume carefully and fix anything "
                "that is not 100% true before you send it to anyone."
            )

    with st.expander("View extracted resume text"):
        st.text(data["raw_text"])