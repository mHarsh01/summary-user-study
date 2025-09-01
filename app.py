import os, csv, random, html
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="Summary User Study", layout="wide")

# ================== STYLES ==================
st.markdown("""
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
""", unsafe_allow_html=True)

# -------- Slide data (replace with your own) --------
slides = [
    {
        "id": "slide1",
        "image": r"D:\Final Desertation\master_llm_project\data\combined\infographicvqa\10087.jpeg",
        "text_summary": "Physical distancing reduces COVID-19 infection risk by 12.8%, with increased distance further lowering risk; evidence certainty is moderate."
                         "\nFace masks or respirators lower infection or transmission risk, but the certainty of evidence is low."
                         "\nEye protection reduces infection risk by 16-55%, with low certainty of evidence."
                         "\nNo single intervention offers complete protection; combining measures and maintaining hand hygiene is essential."
                         "\nFindings are based on a systematic review and meta-analysis published in The Lancet in June 2020.",
        "json_summary": "Physical distancing of 1 meter or more reduces the chance of infection or transmission from 12.8% to 2.6%, with moderate certainty of evidence."
                         "\nWearing face masks or respirators lowers the chance of infection or transmission from 17.4% to 3.1%, but the certainty of evidence is low. "
                         "\nUsing eye protection decreases the chance of infection or transmission from 16.0% to 5.5%, with low certainty of evidence."
                         "\nThe relative effect of physical distancing might increase with every additional meter of distance.",
    },
    {
        "id": "slide2",
        "image": r"D:\Final Desertation\master_llm_project\data\combined\slidevqa\3-140722061229-phpapp01_95_slide10.png",
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
        "image": r"D:\Final Desertation\master_llm_project\data\combined\slidevqa\2015-holiday-prediction-report-151027133029-lva1-app6892_95_slide11.png",
        "text_summary": "Social media primarily drives awareness rather than direct sales for retailers."
                        "\nSocial networks enable targeting of similar consumer profiles who follow the same brands as their friends."
                        "\nIn 2015, social media was expected to drive only 2% of referred visits to retail websites, remaining flat year-over-year."
                        "\nEach social media visit generated about one dollar in revenue on average, with Facebook leading at $1.24 per visit."
                        "\nOther platforms' revenue per visit included Pinterest at $0.74, Twitter at $0.60, and Reddit at $0.57.",
        "json_summary": "Only 2% of visits come from social media sources."
                        "\nFacebook generates the highest referred revenue per visit, increasing from $1.16 in Q3 2014 to $1.24 in Q3 2015."
                        "\nTwitter's referred revenue per visit rose from $0.43 in Q3 2014 to $0.60 in Q3 2015."
                        "\nPinterest's referred revenue per visit increased from $0.66 in Q3 2014 to $0.74 in Q3 2015."
                        "\nReddit showed the largest relative increase in referred revenue per visit, from $0.27 in Q3 2014 to $0.57 in Q3 2015."
    },
    {
        "id": "slide4",
        "image": r"D:\Final Desertation\master_llm_project\data\combined\infographicvqa\11142.jpeg",
        "text_summary": "Use fluid resistant surgical masks and disposable aprons for general contact with confirmed or suspected COVID-19 cases."
                         "\nEye protection should be worn based on risk assessment."
                         "\nFor more information, contact Infection Control at 01889 571837.",
        "json_summary": "Safe PPE for COVID-19 includes a full face shield and an FFP3 face mask for facial protection."
                         "\nHand protection requires wearing gloves."
                         "\nBody protection involves wearing a disposable apron and a long-sleeved fluid repellent gown."
                         "\nA fluid resistant surgical mask is also part of the PPE."
                         "\nEye protection should be worn based on risk assessment."
    },
    {
        "id": "slide5",
        "image": r"D:\Final Desertation\master_llm_project\data\combined\slidevqa\aiesec2015informationbooklet-3-150805123904-lva1-app6891_95_slide18.png",
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
                         "\nRevenue streams come from sponsorship and free offerings, while cost structure includes product costs, online platform, and logistics."
    }
]

results_csv = "results.csv"

# ================== STATE ==================
if "current_slide" not in st.session_state:
    st.session_state.current_slide = 0
if "last_slide" not in st.session_state:
    st.session_state.last_slide = -1
if "order" not in st.session_state:
    st.session_state.order = random.choice([("text", "json"), ("json", "text")])

# ---------- PARTICIPANT ID (assign once per session) ----------
def _next_participant_id(csv_path: str) -> str:
    """
    Reads existing participant IDs from the CSV (if any),
    finds the maximum 'personN', and returns 'person{N+1}'.
    """
    max_n = 0
    if os.path.exists(csv_path):
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    pid = (row.get("participant_id") or "").strip()
                    if pid.startswith("person"):
                        try:
                            n = int(pid.replace("person", ""))
                            if n > max_n:
                                max_n = n
                        except ValueError:
                            pass
        except Exception:
            # If CSV is malformed, safely fall back to person1
            max_n = 0
    return f"person{max_n + 1}"

if "participant_id" not in st.session_state:
    # Assign a new ID only at the start of a fresh session
    st.session_state.participant_id = _next_participant_id(results_csv)

participant_id = st.session_state.participant_id  # reuse for all slides in this session

slide = slides[st.session_state.current_slide]

# randomize order once per slide
if st.session_state.current_slide != st.session_state.last_slide:
    st.session_state.order = random.choice([("text","json"),("json","text")])
    st.session_state.last_slide = st.session_state.current_slide

order = st.session_state.order
summary1_text, summary2_text = (
    (slide["text_summary"], slide["json_summary"]) if order[0]=="text" else
    (slide["json_summary"], slide["text_summary"])
)
summary1_source, summary2_source = order[0], order[1]

def _nl2br_safe(s: str) -> str:
    return html.escape(s).replace("\n", "<br>")

summary1_html = _nl2br_safe(summary1_text)
summary2_html = _nl2br_safe(summary2_text)

# ================== HEADER ==================
st.markdown(
    f'<div id="slide-header"><h3>Slide {st.session_state.current_slide+1} of {len(slides)}</h3></div>',
    unsafe_allow_html=True
)

# ================== SLIDE + SUMMARIES ==================
left, right = st.columns([0.6, 0.4])

with left:
    if os.path.exists(slide["image"]):
        st.image(slide["image"])
    else:
        st.warning(f"Image not found: {slide['image']}")

with right:
    st.markdown('<div class="summary-panel">', unsafe_allow_html=True)
    st.markdown("<h3>Summary 1</h3>", unsafe_allow_html=True)
    st.markdown(f"<div>{summary1_html}</div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3>Summary 2</h3>", unsafe_allow_html=True)
    st.markdown(f"<div>{summary2_html}</div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =============== QUESTIONNAIRE ===============
st.markdown("### Questionnaire")

sid = slide["id"]  # use per-slide keys so answers don't carry over

with st.form(f"survey_{sid}", clear_on_submit=True):
    # Multiple choice (Top/Bottom/Both/Neither)
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

    # Optional rating scales (1–5)
    c1, c2 = st.columns(2)
    with c1:
        clr_top = st.slider("Rate the clarity of the Top summary (1–5)", 1, 5, 1, key=f"clr_top_{sid}")
    with c2:
        clr_bottom = st.slider("Rate the clarity of the Bottom summary (1–5)", 1, 5, 1, key=f"clr_bot_{sid}")

    # Open comments
    q_comment = st.text_area(
        "Why did you choose the summary you preferred?",
        key=f"comment_{sid}",
        placeholder="Write a short explanation…(Open comments)"
    )

    submitted = st.form_submit_button("Submit")

# ================== SAVE & ADVANCE ==================
if submitted:
    # Top/Bottom mapping to your internal sources
    # In this layout, "Top" is the first summary shown on the right panel (summary1),
    # "Bottom" is the second (summary2).
    tb_map   = {"Top": "summary1", "Bottom": "summary2", "Both equally": "both", "Neither": "neither"}
    pref_map = {"Top": "summary1", "Bottom": "summary2"}

    row = {
        "participant_id": participant_id,  # <-- consistent per session
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "image_id": slide["id"],
        "summary1_source": summary1_source,
        "summary2_source": summary2_source,
        "summary_order_randomized": True,

        # new questionnaire fields
        "comprehension_choice": tb_map.get(q_comp),
        "accuracy_choice": tb_map.get(q_acc),
        "preference_choice": pref_map.get(q_pref),
        "clarity_top_1to5": int(clr_top),
        "clarity_bottom_1to5": int(clr_bottom),
        "open_comments": (q_comment or "").strip(),
    }

    file_exists = os.path.exists(results_csv)
    fieldnames = [
        "participant_id","timestamp","image_id",
        "summary1_source","summary2_source","summary_order_randomized",
        "comprehension_choice","accuracy_choice","preference_choice",
        "clarity_top_1to5","clarity_bottom_1to5","open_comments",
    ]

    with open(results_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    st.success(f"✅ Response saved for {slide['id']} as {participant_id}!")
    # (advance to next slide stays the same)

    if st.session_state.current_slide < len(slides)-1:
        st.session_state.current_slide += 1
        st.session_state.order = random.choice([("text","json"),("json","text")])
        st.rerun()
    else:
        st.balloons()
        st.markdown("## 🎉 Thanks for completing the study!")
        st.markdown(f"Your responses were saved to **{results_csv}**.")
