import streamlit as st
from openai import OpenAI, AuthenticationError
from dotenv import load_dotenv
import os
import json

load_dotenv()

st.set_page_config(page_title="Summify — AI Text Summarizer", page_icon="◎", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; background-color: #0D1117 !important; color: #E2E8F0 !important; }
[data-testid="stSidebar"] { background: #161B22 !important; border-right: 1px solid rgba(99,179,237,0.1) !important; }
[data-testid="stSidebar"] * { color: #CBD5E0 !important; }
[data-testid="stSidebar"] h3 { color: #63B3ED !important; font-size: 0.85rem !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; }
[data-testid="stSidebar"] a { color: #63B3ED !important; }
[data-testid="stAppViewContainer"] > .main { background: #0D1117 !important; }
[data-testid="block-container"] { padding-top: 2.5rem !important; }
textarea, .stTextInput input { background: #161B22 !important; border: 1px solid rgba(99,179,237,0.2) !important; border-radius: 10px !important; color: #E2E8F0 !important; font-family: 'Sora', sans-serif !important; font-size: 0.9rem !important; }
textarea:focus, .stTextInput input:focus { border-color: rgba(99,179,237,0.6) !important; box-shadow: 0 0 0 3px rgba(99,179,237,0.08) !important; }
[data-testid="stSelectbox"] > div > div { background: #161B22 !important; border: 1px solid rgba(99,179,237,0.2) !important; border-radius: 10px !important; color: #E2E8F0 !important; }
.stButton > button { background: linear-gradient(135deg, #2B6CB0, #3182CE) !important; color: white !important; border: none !important; border-radius: 10px !important; font-family: 'Sora', sans-serif !important; font-weight: 500 !important; font-size: 0.9rem !important; padding: 0.6rem 2rem !important; width: 100% !important; letter-spacing: 0.02em !important; box-shadow: 0 4px 15px rgba(49,130,206,0.3) !important; }
.stButton > button:hover { background: linear-gradient(135deg, #3182CE, #4299E1) !important; box-shadow: 0 6px 20px rgba(49,130,206,0.45) !important; }
[data-testid="stAlert"] { background: rgba(99,179,237,0.07) !important; border: 1px solid rgba(99,179,237,0.25) !important; border-radius: 10px !important; color: #90CDF4 !important; }
hr { border-color: rgba(99,179,237,0.1) !important; }
.page-title { font-size: 1.9rem; font-weight: 600; color: #EBF8FF; letter-spacing: -0.03em; line-height: 1.2; }
.page-title span { background: linear-gradient(90deg, #63B3ED, #76E4F7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.page-subtitle { font-size: 0.72rem; font-weight: 400; color: #4A5568; letter-spacing: 0.12em; text-transform: uppercase; margin-top: 4px; margin-bottom: 2rem; }
.card { background: #161B22; border: 1px solid rgba(99,179,237,0.12); border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; position: relative; overflow: hidden; }
.card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #2B6CB0, #76E4F7, transparent); opacity: 0.6; }
.card-label { font-size: 0.62rem; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: #4A6FA5; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 6px; }
.card-label::before { content: ''; display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #63B3ED; opacity: 0.7; }
.summary-text { font-size: 0.95rem; line-height: 1.8; color: #CBD5E0; font-weight: 300; }
.one-liner-text { font-size: 1rem; line-height: 1.7; color: #90CDF4; font-style: italic; font-weight: 300; }
.tag { display: inline-block; background: rgba(43,108,176,0.18); color: #90CDF4; border: 1px solid rgba(99,179,237,0.2); font-size: 0.7rem; font-weight: 500; padding: 4px 12px; border-radius: 20px; margin: 3px 3px 3px 0; font-family: 'JetBrains Mono', monospace; }
.meta-grid { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.meta-item { background: rgba(22,27,34,0.8); border: 1px solid rgba(99,179,237,0.1); border-radius: 10px; padding: 0.9rem 1.1rem; flex: 1; min-width: 90px; }
.meta-val { font-size: 1.3rem; font-weight: 600; color: #EBF8FF; font-family: 'JetBrains Mono', monospace; }
.meta-key { font-size: 0.6rem; letter-spacing: 0.1em; text-transform: uppercase; color: #4A6FA5; margin-top: 4px; }
.sentiment-positive { background: rgba(39,103,73,0.2); color: #68D391; border: 1px solid rgba(104,211,145,0.25); padding: 4px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 500; display: inline-block; }
.sentiment-neutral { background: rgba(74,106,165,0.2); color: #90CDF4; border: 1px solid rgba(144,205,244,0.25); padding: 4px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 500; display: inline-block; }
.sentiment-negative { background: rgba(155,44,44,0.2); color: #FC8181; border: 1px solid rgba(252,129,129,0.25); padding: 4px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 500; display: inline-block; }
[data-testid="stCode"] { background: #0D1117 !important; border: 1px solid rgba(99,179,237,0.1) !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">◎ Summ<span>ify</span></div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">AI-Powered Text Summarizer &nbsp;·&nbsp; Built with OpenAI API</div>', unsafe_allow_html=True)
st.divider()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_summary(text: str, length: str, api_key: str) -> dict:
    length_map = {
        "Short (2-3 sentences)":     "2-3 sentences",
        "Medium (1 paragraph)":      "1 short paragraph (4-6 sentences)",
        "Detailed (2-3 paragraphs)": "2-3 paragraphs",
    }
    prompt = f"""You are a professional summarization assistant.
Analyze the text below and respond ONLY with a valid JSON object — no preamble, no markdown fences.

JSON schema:
{{
  "summary": "string — {length_map[length]}",
  "keywords": ["array of 5-8 key terms or phrases"],
  "sentiment": "positive" | "neutral" | "negative",
  "one_liner": "string — single sentence capturing the core idea"
}}

Text:
\"\"\"
{text}
\"\"\"
"""
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a precise summarization assistant. Always respond with valid JSON only."},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.3,
        max_tokens=1024,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content.strip())


def word_count(text): return len(text.split())
def read_time(wc): return f"{max(1, round(wc / 200))} min"


with st.sidebar:
    st.markdown("### ⚙ Settings")
    st.markdown("**Model**")
    st.caption("Using `gpt-4o-mini` — fast, accurate.")
    st.divider()
    st.markdown("**How it works**")
    st.caption("1. Paste any text\n2. Choose summary length\n3. Hit Summarise\n4. Get structured output")
    st.divider()
    st.caption("Built with [Streamlit](https://streamlit.io) + [OpenAI API](https://platform.openai.com)")

api_key = OPENAI_API_KEY


input_text = st.text_area("Input", placeholder="Paste any article, document, email, or block of text…", height=220, label_visibility="collapsed")

col1, col2 = st.columns([2, 1])
with col1:
    length = st.selectbox("Length", ["Short (2-3 sentences)", "Medium (1 paragraph)", "Detailed (2-3 paragraphs)"], label_visibility="collapsed")
with col2:
    run = st.button("Summarise →")

if run:
    if not input_text.strip():
        st.warning("Please paste some text first.")
    else:
        with st.spinner("Summarising…"):
            try:
                result    = get_summary(input_text.strip(), length, api_key)
                wc        = word_count(input_text)
                rt        = read_time(wc)
                sentiment = result.get("sentiment", "neutral").lower()

                st.markdown(f'<div class="card"><div class="card-label">Core idea</div><div class="one-liner-text">"{result.get("one_liner", "")}"</div></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="card"><div class="card-label">Summary</div><div class="summary-text">{result.get("summary", "")}</div></div>', unsafe_allow_html=True)

                tags_html = "".join(f'<span class="tag">{kw}</span>' for kw in result.get("keywords", []))
                st.markdown(f'<div class="card"><div class="card-label">Keywords</div><div style="margin-top:4px;">{tags_html}</div></div>', unsafe_allow_html=True)

                icons = {"positive": "● Positive", "neutral": "● Neutral", "negative": "● Negative"}
                st.markdown(f"""
                <div class="card"><div class="card-label">Analysis</div>
                <div class="meta-grid">
                  <div class="meta-item"><div class="meta-val">{wc:,}</div><div class="meta-key">Word count</div></div>
                  <div class="meta-item"><div class="meta-val">{rt}</div><div class="meta-key">Read time</div></div>
                  <div class="meta-item"><div class="meta-key" style="margin-bottom:8px;">Sentiment</div><span class="sentiment-{sentiment}">{icons.get(sentiment, sentiment)}</span></div>
                </div></div>""", unsafe_allow_html=True)

                st.markdown('<p style="font-size:0.62rem;letter-spacing:0.12em;text-transform:uppercase;color:#4A6FA5;margin-bottom:4px;">Copy summary</p>', unsafe_allow_html=True)
                st.code(result.get("summary", ""), language=None)

            except json.JSONDecodeError:
                st.error("Could not parse the API response. Please try again.")
            except AuthenticationError:
                st.error("Invalid API key. Please check your OpenAI API key in the sidebar.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")
