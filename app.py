# app_with_square_cards.py
import streamlit as st
from main import (
    extract_text_from_pdfs, ask_gemini, simplify_text, summarize_text,
    translate_text, detect_document_type, extract_key_entities,
    generate_compliance_checklist, explain_complex_terms, risk_assessment
)

st.set_page_config(page_title="Legal Document AI Assistant", page_icon="⚖️", layout="wide")

# ---------- Styling (fonts, colors, square card style) ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    :root{
        --bg:#f6f8fb;
        --card:#ffffff;
        --muted:#6b7280;
        --primary-1:#6f42c1;
        --primary-2:#4f46e5;
        --accent:#10b981;
    }

    .stApp { background: linear-gradient(180deg,var(--bg), #f0f4ff); font-family: 'Poppins', sans-serif; color: #0f172a; }

    /* header */
    .main-header { background: linear-gradient(90deg,var(--primary-1),var(--primary-2)); color: white !important; padding:20px; border-radius:10px; box-shadow:0 8px 30px rgba(79,70,229,0.12); margin-bottom:16px;}
    .main-header h1{ margin:0; font-size:24px; }
    .main-header p{ margin:6px 0 0; opacity:0.95; }

    /* square-grid container */
    .analysis-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 18px;
        margin-top: 12px;
    }

    /* Make Streamlit buttons look like square cards (affects buttons globally).
       If you have other buttons, they will also get this style — tweak as needed. */
    .stButton > button {
        width: 100%;
        height: 180px;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        font-weight: 600;
        font-size: 15px;
        color: white;
        border: none;
        box-shadow: 0 10px 30px rgba(15,23,42,0.08);
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    .stButton > button:hover {
        transform: translateY(-6px);
        box-shadow: 0 18px 45px rgba(15,23,42,0.14);
    }

    /* individual card colors */
    .card-key { background: linear-gradient(90deg,#34d399,#10b981); }     /* green */
    .card-check { background: linear-gradient(90deg,#60a5fa,#3b82f6); }   /* blue */
    .card-risk { background: linear-gradient(90deg,#fb7185,#ef4444); }    /* red */
    .card-terms { background: linear-gradient(90deg,#f59e0b,#f97316); }   /* orange */
    .card-summary { background: linear-gradient(90deg,#a78bfa,#7c3aed); } /* purple */
    .card-translate { background: linear-gradient(90deg,#06b6d4,#3b82f6);}/* teal */

    /* small icon styling inside label */
    .card-emoji { font-size: 32px; margin-bottom:8px; }
    .card-title { font-size: 15px; line-height:1.1; }

    /* responsive adjustments */
    @media (max-width: 640px) {
        .stButton > button { height:160px; font-size:14px; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Header ----------
st.markdown(
    """
    <div class="main-header">
        <h1>Demystify The Legal Document </h1>
        <p>Upload documents and use the square tools below for quick domain-specific analysis.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- Sidebar: basic upload + language ----------
with st.sidebar:
    st.header("📂 Upload & Settings")
    uploaded_files = st.file_uploader("Upload PDF(s)", type=["pdf"], accept_multiple_files=True)
    language = st.selectbox("Answer language", ["English", "Hindi", "Marathi"], index=0)
    if st.button("🗑️ Clear Session"):
        for k in ['pdf_text', 'doc_type', 'chat_history']:
            if k in st.session_state:
                del st.session_state[k]
        st.experimental_rerun()

# ---------- Initialize session ----------
if "pdf_text" not in st.session_state: st.session_state.pdf_text = ""
if "doc_type" not in st.session_state: st.session_state.doc_type = ""
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# ---------- Process uploads ----------
if uploaded_files and not st.session_state.pdf_text:
    with st.spinner("Processing documents..."):
        st.session_state.pdf_text = extract_text_from_pdfs(uploaded_files)
        st.session_state.doc_type = detect_document_type(st.session_state.pdf_text)
    st.success("Document processing complete!")
    st.balloons()

# ---------- Show doc type (if any) ----------
if st.session_state.doc_type:
    st.markdown(f"<div style='margin-top:10px;'><strong>Document type:</strong> {st.session_state.doc_type}</div>", unsafe_allow_html=True)

# ---------- Analysis square cards (grid) ----------
st.markdown("<h3 style='margin-top:18px;'>Quick Analysis Tools</h3>", unsafe_allow_html=True)
st.markdown("<div class='analysis-grid'>", unsafe_allow_html=True)

# Row of square buttons (each will be styled as a square via CSS above)
# Note: each button must have unique key to avoid Streamlit duplicate key errors.

# 1 Key Information
if st.button("\nKey Information", key="btn_key", help="Extract key parties, dates, obligations", ):
    if not st.session_state.pdf_text:
        st.warning("Upload a document first.")
    else:
        with st.spinner("Extracting key information..."):
            res = extract_key_entities(st.session_state.pdf_text, st.session_state.doc_type)
            if language != "English":
                res = translate_text(res, language)
            st.session_state.chat_history.append(("Key Information", res))
            st.success("Key information extracted")

# 2 Action Checklist
if st.button("\nAction Checklist", key="btn_check", help="Generate practical checklist for compliance"):
    if not st.session_state.pdf_text:
        st.warning("Upload a document first.")
    else:
        with st.spinner("Generating checklist..."):
            res = generate_compliance_checklist(st.session_state.pdf_text, st.session_state.doc_type)
            if language != "English":
                res = translate_text(res, language)
            st.session_state.chat_history.append(("Action Checklist", res))
            st.success("Checklist generated")

# 3 Risk Assessment
if st.button("\nRisk Assessment", key="btn_risk", help="Identify potential risks and issues"):
    if not st.session_state.pdf_text:
        st.warning("Upload a document first.")
    else:
        with st.spinner("Running risk assessment..."):
            res = risk_assessment(st.session_state.pdf_text, st.session_state.doc_type)
            if language != "English":
                res = translate_text(res, language)
            st.session_state.chat_history.append(("Risk Assessment", res))
            st.success("Risk assessment complete")

# 4 Explain Terms
if st.button("\nExplain Terms", key="btn_terms", help="Explain complex/legal terms in plain language"):
    if not st.session_state.pdf_text:
        st.warning("Upload a document first.")
    else:
        with st.spinner("Explaining terms..."):
            res = explain_complex_terms(st.session_state.pdf_text, st.session_state.doc_type)
            if language != "English":
                res = translate_text(res, language)
            st.session_state.chat_history.append(("Explain Terms", res))
            st.success("Terms explained")

# 5 Summary
if st.button("  \nSummary  ", key="btn_summary", help="Generate a concise comprehensive summary"):
    if not st.session_state.pdf_text:
        st.warning("Upload a document first.")
    else:
        with st.spinner("Summarizing..."):
            res = summarize_text(st.session_state.pdf_text, st.session_state.doc_type)
            if language != "English":
                res = translate_text(res, language)
            st.session_state.chat_history.append(("Summary", res))
            st.success("Summary generated")

# 6 Translate Document (optional quick tool)
if st.button("  \nTranslate  ", key="btn_translate", help="Translate extracted content to chosen language"):
    if not st.session_state.pdf_text:
        st.warning("Upload a document first.")
    else:
        with st.spinner("Translating..."):
            res = translate_text(st.session_state.pdf_text[:4000], language)  # translate excerpt
            st.session_state.chat_history.append(("Translation", res))
            st.success("Translation complete")

st.markdown("</div>", unsafe_allow_html=True)

# ---------- Show conversation/history/cards content in squares? ----------
# Display recent results with card-like boxes (not square, these are results)
if st.session_state.chat_history:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3>Results</h3>", unsafe_allow_html=True)
    # show latest at top
    for title, content in reversed(st.session_state.chat_history):
        st.markdown(f"{title}")
        st.text_area(label="", value=content, height=220, key=f"ta_{hash(title+content) % 1_000_000}")

# footer
st.markdown("---")
st.markdown("<div style='text-align:center; color:#6b7280'>Made with ❤️ — AI Document Assistant</div>", unsafe_allow_html=True)
