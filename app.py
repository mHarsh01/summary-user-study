import os
import random
import html
from datetime import datetime
from pathlib import Path

import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials  # ok if you already use this

st.set_page_config(page_title="Summary User Study", layout="wide")

# ================== GOOGLE SHEETS SETUP ==================
SHEET_NAME = "YOUR_SHEET_NAME_HERE"   # <-- change this to your actual sheet name

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Auth: expects Streamlit secret "gcp_service_account" (a dict)
try:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME)
    participants_ws = sheet.worksheet("participants")
    responses_ws = sheet.worksheet("responses")
except Exception as e:
    st.error(
        "Google Sheets setup failed. Check your `SHEET_NAME`, "
        "worksheet tabs (`participants`, `responses`), and Streamlit secrets.\n\n"
        f"Details: {e}"
    )
    st.stop()

# ================== HELPERS ==================
def norm_path(p: str) -> str:
    """Normalize to a POSIX-like path Streamlit can find on any OS."""
    return str(Path(p))

def get_next_participant_id() -> str:
    """Read participants tab, assign next ID, and record it."""
    try:
        ids = participants_ws.col_values(1)[1:]  # skip header
    except Exception as e:
        st.error(f"Failed to read participants sheet: {e}")
        st.stop()

    if not ids:
        next_id = "person1"
    else:
        nums = [int(x.replace("person", "")) for x in ids if x.startswith("person")]
        next_id = f"person{(max(nums) + 1) if nums else 1}"

    try:
        participants_ws.append_row([next_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    except Exception as e:
        st.error(f"Failed to write participant ID: {e}")
        st.stop()

    return next_id

def _nl2br_safe(s: str) -> str:
    return html.escape(s).replace("\n", "<br>")

# ================== STATE ==================
if "current_slide" not in st.session_state:
    st.session_state.current_slide = 0
if "last_slide" not in st.session_state:
    st.session_state.last_slide = -1
if "order" not in st.session_state:
    st.session_state.order = random.choice([("text", "json"), ("json", "text")])
if "participant_id" not in st.session_state:
    st.session_state.participant_id = get_next_participant_id()

participant_id = st.session_state.participant_id

# ================== STYLES ==================
st.markdown(
    """
<style>
:root { --gap: 20px; --hdr-h: 56px; }
.block-container { padding-top: 0.5rem; }
#slide-header {
  position: sticky; top: 0; z-index: 1000;
  padding: 8px 0 10px 0; margin-bottom: var(--gap);
  background: inherit;
}
#slide-header h3 { margin: 0; }
.summary-panel { padding: 8px 12px; border-radius: 8px; background: inherit; }
hr { opacity: .25; }
</style>
""",
    unsafe_allow_html=True,
)

# -------- Slide data (replace with your own) --------
slides = [
    {
        "id": "slide1",
        # FIX: backslash escapes -> use forward slashes or raw string
        "image": norm_path("images/10087.jpeg"),
        "text_summary": "Physical distancing reduces COVID-19 infection risk by 12.8%, with increased distance further lowering risk; evidence certainty is moderate."
                        "\nFace masks or respirators lower infection or transmission risk, but the certainty of evidence is low."
                        "\nEye protection reduces infection risk by 16-55%, with low certainty of evidence."
                        "\nNo single intervention offers complete protection; combining measures and maintaining hand hygiene is essential."
                        "\nFindings are based on a systematic review and meta-analysis published in The Lancet in June 2020.",
        "json_summary": "Physical distancing of 1 meter or more reduces the chance of infection or transmission from 12.8% to 2.6%, with moderate certainty of evidence."
                        "\nWearing face masks or respirators lowers the chance of infection or transmission from 17.4% to 3.1%, but the certainty of evidence is low."
                        "\nUsing eye protection decreases the chance of infection or transmission from 16.0% to 5.5%, with low certainty of evidence."
                        "\nThe relative effect of physical distancing might increase with every additional meter of distance.",
    },
    {
        "id": "slide2",
        "image": norm_path("images/3-140722061229-phpapp01_95_slide10.png"),
        "text_summary": "Brand building drives long-term sales growth."
                        "\nSales activation leads to short-term sales uplifts."
                        "\nSales activation does not contribute to long-term growth."
                        "\nShort-term effects of sales activation dominate for approximately 6 months.",
        "json_summary": "Sales activation leads to short-term sales uplifts but does not contribute to long-term growth."
                        "\nBrand building results in long-term sales growth over time."
                        "\nShort-term effects from sales activation dominate for approximately six months."
                        "\nThe graph illustrates the contrast between temporary sales spikes from activation and sustained growth from brand building.",
    },
    {
        "id": "slide3",
        "image": norm_path("images/2015-holiday-prediction-report-151027133029-lva1-app6892_95_slide11.png"),
        "text_summary": "Social media primarily drives awareness rather than direct sales for retailers."
                        "\nSocial networks enable targeting of similar consumer profiles who follow the same brands as their friends."
                        "\nIn 2015, social media was expected to drive only 2% of referred visits to retail websites, remaining flat year-over-year."
                        "\nEach social media visit generated about one dollar in revenue on average, with Facebook leading at $1.24 per visit."
                        "\nOther platforms' revenue per visit included Pinterest at $0.74, Twitter at $0.60, and Reddit at $0.57.",
        "json_summary": "Only 2% of visits come from social media sources."
                        "\nFacebook generates the highest referred revenue per visit, increasing from $1.16 in Q3 2014 to $1.24 in Q3 2015."
                        "\nTwitter's referred revenue per visit rose from $0.43 in Q3 2014 to $0.60 in Q3 2015."
                        "\nPinterest's referred revenue per visit increased from $0.66 in Q3 2014 to $0.74 in Q3 2015."
                        "\nReddit showed the largest relative increase in referred revenue per visit, from $0.27 in Q3 2014 to $0.57 in Q3 2015.",
    },
    {
        "id": "slide4",
        "image": norm_path("images/11142.jpeg"),
        "text_summary": "Use fluid resistant surgical masks and disposable aprons for general contact with confirmed or suspected COVID-19 cases."
                        "\nEye protection should be worn based on risk assessment."
                        "\nFor more information, contact Infection Control at 01889 571837.",
        "json_summary": "Safe PPE for COVID-19 includes a full face shield and an FFP3 face mask for facial protection."
                        "\nHand protection requires wearing gloves."
                        "\nBody protection involves wearing a disposable apron and a long-sleeved fluid repellent gown."
                        "\nA fluid resistant surgical mask is also part of the PPE."
                        "\nEye protection should be worn based on risk assessment.",
    },
    {
        "id": "slide5",
        "image": norm_path("images/aiesec2015informationbooklet-3-150805123904-lva1-app6891_95_slide18.png"),
        "text_summary": "The Team Member programme targets universities and young people, offering membership access to a diverse group."
                        "\nKey activities include recruitment, training, and delivering practical experience."
                        "\nValue propositions focus on providing practical experience, hard skills, and access to a global network."
                        "\nCustomer relationships are maintained through online platforms and alumni networks."
                        "\nRevenue streams include sponsorships, while cost structure involves product development, online platform, and logistics.",
        "json_summary": "Key partners include universities, training partners, and alumni."
                        "\nKey activities focus on recruitment, membership management, product packaging, sales delivery, and education & training."
                        "\nValue propositions emphasize targeted access to diverse young people, practical team experience, global network access, and hard-skills development."
                        "\nCustomer relationships are maintained through membership and account management."
                        "\nCustomer segments target organizations and young people."
                        "\nRevenue streams come from sponsorship and free offerings, while cost structure includes product costs, online platform, and logistics.",
    },
]

slide = slides[st.session_state.current_slide]

# Randomize order once per slide
if st.session_state.current_slide != st.session_state.last_slide:
    st.session_state.order = random.choice([("text", "json"), ("json", "text")])
    st.session_state.last_slide = st.session_state.current_slide

order = st.session_state.order
summary1_text, summary2_text = (
    (slide["text_summary"], slide["json_summary"]) if order[0] == "text" else
    (slide["json_summary"], slide["text_summary"])
)
summary1_source, summary2_source = order[0], order[1]

summary1_html = _nl2br_safe(summary1_text)
summary2_html = _nl2br_safe(summary2_text)

# ================== HEADER ==================
st.markdown(
    f'<div id="slide-header"><h3>Slide {st.session_state.current_slide + 1} of {len(slides)}</h3></div>',
    unsafe_allow_html=True,
)

# ================== SLIDE + SUMMARIES ==================
left, right = st.columns([0.6, 0.4])

with left:
    img_path = slide["image"]
    # If absolute Windows paths are used, this warns usefully on other machines
    if os.path.exists(img_path):
        st.image(img_path)
    else:
        st.warning(f"Image not found: {img_path}")

with right:
    st.markdown('<div class="summary-panel">', unsafe_allow_html=True)
    st.markdown("<h3>Summary 1</h3>", unsafe_allow_html=True)
    st.markdown(f"<div>{summary1_html}</div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3>Summary 2</h3>", unsafe_allow_html=True)
    st.markdown(f"<div>{summary2_html}</div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =============== QUESTIONNAIRE ===============
st.markdown("### Questionnaire")

sid = slide["id"]

with st.form(f"survey_{sid}", clear_on_submit=True):
    # NOTE: index=None is supported on modern Streamlit to allow no default selection.
    q_comp = st.radio(
        "Which summary helps you understand the slide better?",
        ["Top", "Bottom", "Both equally", "Neither"],
        index=None,
        key=f"comp_{sid}",
    )
    q_acc = st.radio(
        "Which summary reflects the slide content more accurately?",
        ["Top", "Bottom", "Both equally", "Neither"],
        index=None,
        key=f"acc_{sid}",
    )
    q_pref = st.radio(
        "If you had to keep only one summary, which one would you keep?",
        ["Top", "Bottom"],
        index=None,
        key=f"pref_{sid}",
    )

    c1, c2 = st.columns(2)
    with c1:
        clr_top = st.slider("Rate the clarity of the Top summary (1–5)", 1, 5, 1, key=f"clr_top_{sid}")
    with c2:
        clr_bottom = st.slider("Rate the clarity of the Bottom summary (1–5)", 1, 5, 1, key=f"clr_bot_{sid}")

    q_comment = st.text_area(
        "Why did you choose the summary you preferred?",
        key=f"comment_{sid}",
        placeholder="Write a short explanation…(Open comments)",
    )

    submitted = st.form_submit_button("Submit")

# ================== SAVE & ADVANCE ==================
if submitted:
    tb_map   = {"Top": "summary1", "Bottom": "summary2", "Both equally": "both", "Neither": "neither"}
    pref_map = {"Top": "summary1", "Bottom": "summary2"}

    row = [
        participant_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        slide["id"],
        summary1_source,
        summary2_source,
        True,  # keep if your 'responses' header expects a boolean flag
        tb_map.get(q_comp),
        tb_map.get(q_acc),
        pref_map.get(q_pref),
        int(clr_top),
        int(clr_bottom),
        (q_comment or "").strip(),
    ]

    try:
        responses_ws.append_row(row)
    except Exception as e:
        st.error(f"Failed to save response: {e}")
        st.stop()

    st.success(f"✅ Response saved for {slide['id']} as {participant_id}!")

    if st.session_state.current_slide < len(slides) - 1:
        st.session_state.current_slide += 1
        st.session_state.order = random.choice([("text", "json"), ("json", "text")])
        st.rerun()
    else:
        st.balloons()
        st.markdown("## 🎉 Thanks for completing the study!")
        st.markdown("Your responses were saved to Google Sheets.")
