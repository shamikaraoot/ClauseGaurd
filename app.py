import streamlit as st
import pandas as pd
from datetime import datetime
from googletrans import Translator
import os
from googletrans import Translator


translator = Translator()

def t(text, lang_code):
    if lang_code == "en":
        return text
    return translator.translate(text, dest=lang_code).text


import asyncio

async def t_async(text, lang_code):
    if lang_code == "en":
        return text
    return await translator.translate(text, dest=lang_code)

def t(text, lang_code):
    # run async code inside sync context
    return asyncio.run(t_async(text, lang_code))

# ---------- App Config ----------
st.set_page_config(page_title="Viveka - Aadhaar-DBT Awareness", page_icon="🪪", layout="wide")

# ---------- Theming: Background (non-white, soothing – no pinks) ----------
custom_css = """
<style>
  :root {
    /* Dark, soothing gradient (navy to deep teal), no pinks */
    --bg-start: #0b1220;    /* deep navy */
    --bg-end:   #0e2a2a;    /* deep teal */
    --sidebar-start: #101827; /* slightly lighter for sidebar */
    --sidebar-end:   #0f2430;
    --text-color: #f8fafc;  /* near-white for contrast */
    --muted-text: #cbd5e1;  /* slate-300 */
    --card-bg: rgba(15, 23, 42, 0.4); /* translucent slate */
    /* Button theme (choose one palette). Options: light green / dull yellow / red */
    /* Muted slate button palette (eye-comfort, low saturation) */
    --btn-bg: #6b7280;         /* slate-500 */
    --btn-bg-hover: #4b5563;   /* slate-600 */
    --btn-bg-active: #374151;  /* slate-700 */
    --btn-text: #f8fafc;       /* near-white for readability */
    --btn-border: #1f2937;     /* slate-800 border */
  }

  .stApp {
    background: linear-gradient(135deg, var(--bg-start), var(--bg-end));
    color: var(--text-color);
  }

  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--sidebar-start), var(--sidebar-end));
  }

  /* Main blocks subtle translucency over gradient */
  .block-container { background: transparent; }
  section.main > div { background: transparent; }

  /* Tabs bar area */
  div[role="tablist"] { background: transparent; }
  button[role="tab"] { color: var(--muted-text); }
  button[role="tab"][aria-selected="true"] { color: var(--text-color); }

  /* Cards/alerts subtle translucency */
  .stAlert, .stInfo, .stSuccess, .stError, .stWarning {
    background: var(--card-bg) !important;
    color: var(--text-color) !important;
    border: 1px solid rgba(203, 213, 225, 0.15);
    box-shadow: 0 4px 24px rgba(0,0,0,0.25);
    backdrop-filter: saturate(120%) blur(2px);
  }

  /* Text elements */
  h1, h2, h3, h4, h5, h6, p, span, label { color: var(--text-color); }
  .stMarkdown, .markdown-text-container { color: var(--text-color); }

  /* Inputs */
  .stTextInput, .stSelectbox, .stRadio, .stButton button {
    color: var(--text-color);
  }

  /* Unified button styling */
  .stButton > button,
  div[role="button"],
  button[kind],
  button[aria-pressed] {
    background: var(--btn-bg) !important;
    color: var(--btn-text) !important;
    border: 1px solid var(--btn-border) !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.25);
  }
  .stButton > button:hover,
  div[role="button"]:hover,
  button[kind]:hover {
    background: var(--btn-bg-hover) !important;
  }
  .stButton > button:active,
  div[role="button"]:active,
  button[kind]:active {
    background: var(--btn-bg-active) !important;
  }
  .stButton > button:focus-visible,
  div[role="button"]:focus-visible,
  button[kind]:focus-visible {
    outline: 2px solid rgba(34, 197, 94, 0.6) !important; /* green glow */
    outline-offset: 2px;
  }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------- Translator Setup ----------
translator = Translator()
LANG_OPTIONS = {
    "English": "en",
    "हिन्दी (Hindi)": "hi",
    "मराठी (Marathi)": "mr",
    "తెలుగు (Telugu)": "te",
    "ಕನ್ನಡ (Kannada)": "kn",
}

# Preferred manual translations for Hindi to ensure reliability
HINDI_TRANSLATIONS = {
    "📖 Information": "📖 जानकारी",
    "🎯 Quiz": "🎯 प्रश्नोत्तरी",
    "🎥 Video": "🎥 वीडियो",
    "🔗 Resources": "🔗 संसाधन",
    "📝 Feedback": "📝 प्रतिक्रिया",
    "Aadhaar-linked vs DBT-enabled Aadhaar-seeded Bank Accounts": "आधार-लिंक्ड बनाम डीबीटी-सक्षम (आधार-सीडेड) बैंक खाते",
    "What is the difference?": "अंतर क्या है?",
    "Aadhaar-linked bank account means your bank has linked your Aadhaar number for KYC or identification.\n\nDBT-enabled Aadhaar-seeded account means your Aadhaar is properly seeded and marked as 'DBT-enabled' in the NPCI mapper, so government Direct Benefit Transfer (DBT) payments can be credited to this account.": "आधार-लिंक्ड बैंक खाता का अर्थ है कि आपके बैंक ने केवाईसी/पहचान के लिए आपका आधार नंबर लिंक किया है।\n\nडीबीटी-सक्षम (आधार-सीडेड) खाता का अर्थ है कि आपका आधार सही तरीके से सीड किया गया है और एनपीसीआई मैपर में 'डीबीटी-सक्षम' के रूप में दर्ज है, जिससे सरकारी डीबीटी भुगतान सीधे इसी खाते में आएंगे।",
    "Steps to check Aadhaar–bank mapping (NPCI Mapper)": "आधार–बैंक मैपिंग (एनपीसीआई मैपर) जांचने के चरण",
    "Visit the official UIDAI/Bank Mapper service.": "आधिकारिक यूआईडीएआई/बैंक मैपर सेवा पर जाएँ।",
    "Use your Aadhaar number and an OTP sent to your registered mobile.": "अपने आधार नंबर और पंजीकृत मोबाइल पर भेजे गए ओटीपी का उपयोग करें।",
    "Confirm which bank account is mapped for DBT.": "देखें कि डीबीटी के लिए कौन सा बैंक खाता मैप है।",
    "If needed, visit your bank to seed/update Aadhaar for DBT.": "जरूरत हो तो डीबीटी के लिए आधार सीड/अपडेट कराने बैंक जाएँ।",
    "Important Links": "महत्वपूर्ण लिंक",
    "Awareness Video": "जागरूकता वीडियो",
    "Replace this with your Canva-made explainer later.": "बाद में इसे अपने कैनवा एक्सप्लेनर से बदलें।",
    "Quick Awareness Quiz": "त्वरित जागरूकता प्रश्नोत्तरी",
    "Choose one": "एक विकल्प चुनें",
    "Correct!": "सही!",
    "Incorrect.": "गलत।",
    "Resources": "संसाधन",
    "Official portals for information and services:": "सूचना और सेवाओं के लिए आधिकारिक पोर्टल:",
    "Never share Aadhaar/OTP publicly. Use only official portals.": "आधार/ओटीपी कभी सार्वजनिक रूप से साझा न करें। केवल आधिकारिक पोर्टल का उपयोग करें।",
    "Never share Aadhaar/OTP publicly, use only official portals.": "आधार/ओटीपी कभी सार्वजनिक रूप से साझा न करें, केवल आधिकारिक पोर्टल का उपयोग करें।",
    "Feedback / Help Request": "प्रतिक्रिया / सहायता अनुरोध",
    "Name": "नाम",
    "State": "राज्य",
    "Telangana": "तेलंगाना",
    "Karnataka": "कर्नाटक",
    "Other": "अन्य",
    "Need Help?": "सहायता चाहिए?",
    "Yes": "हाँ",
    "No": "नहीं",
    "Optional contact (phone/email)": "वैकल्पिक संपर्क (फोन/ईमेल)",
    "Submit": "जमा करें",
    "Thank you! Your response has been recorded.": "धन्यवाद! आपकी प्रतिक्रिया दर्ज कर ली गई है।",
    "Could not save feedback. Please try again.": "प्रतिक्रिया सहेजी नहीं जा सकी। कृपया पुनः प्रयास करें।",
    "This is an awareness prototype for demonstration/education.": "यह प्रदर्शन/शिक्षा के लिए एक जागरूकता प्रोटोटाइप है।",
    "Question": "प्रश्न",
    "Where is DBT enablement recorded for Aadhaar?": "आधार के लिए डीबीटी सक्षम कहाँ दर्ज होता है?",
    "At NPCI mapper": "एनपीसीआई मैपर पर",
    "Only on your ATM card": "केवल आपके एटीएम कार्ड पर",
    "Only at State scholarship portal": "केवल राज्य छात्रवृत्ति पोर्टल पर",
    "To check which bank is mapped for DBT, you should use:": "डीबीटी के लिए कौन सा बैंक मैप है, यह जांचने के लिए आपको उपयोग करना चाहिए:",
    "Any public forum": "कोई भी सार्वजनिक मंच",
    "Official UIDAI/Bank Mapper with OTP": "ओटीपी के साथ आधिकारिक यूआईडीएआई/बैंक मैपर",
    "Random third-party app": "कोई रैंडम थर्ड-पार्टी ऐप",
}


def t(text: str, target_lang_code: str) -> str:
    """Translate text to the selected language using googletrans. Prefer manual Hindi map when available."""
    if not text:
        return text
    try:
        if target_lang_code == "en":
            return text
        if target_lang_code == "hi":
            mapped = HINDI_TRANSLATIONS.get(text)
            if mapped:
                return mapped
        result = translator.translate(text, dest=target_lang_code)
        return result.text
    except Exception:
        return text


# ---------- Session State for Language Selection ----------
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = None
if 'lang_code' not in st.session_state:
    st.session_state.lang_code = None


# ---------- Landing Page with Language Selection ----------
if st.session_state.selected_language is None:
    st.title("🪪 Viveka - Aadhaar-DBT Awareness")
    st.markdown("---")
    
    st.markdown("### Choose your language / अपनी भाषा चुनें / तुमची भाषा निवडा / మీ భాషను ఎంచుకోండి / ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ")
    
    # Priority order: English, Hindi, Telugu, then alphabetical (Kannada, Marathi)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🇺🇸 English", use_container_width=True, type="primary"):
            st.session_state.selected_language = "English"
            st.session_state.lang_code = "en"
            st.rerun()
    
    with col2:
        if st.button("🇮🇳 हिन्दी (Hindi)", use_container_width=True):
            st.session_state.selected_language = "हिन्दी (Hindi)"
            st.session_state.lang_code = "hi"
            st.rerun()
    
    with col3:
        if st.button("🇮🇳 తెలుగు (Telugu)", use_container_width=True):
            st.session_state.selected_language = "తెలుగు (Telugu)"
            st.session_state.lang_code = "te"
            st.rerun()
    
    col4, col5 = st.columns(2)
    
    with col4:
        if st.button("🇮🇳 ಕನ್ನಡ (Kannada)", use_container_width=True):
            st.session_state.selected_language = "ಕನ್ನಡ (Kannada)"
            st.session_state.lang_code = "kn"
            st.rerun()
    
    with col5:
        if st.button("🇮🇳 मराठी (Marathi)", use_container_width=True):
            st.session_state.selected_language = "मराठी (Marathi)"
            st.session_state.lang_code = "mr"
            st.rerun()
    
    st.markdown("---")
    st.info("🛡️ **Security Notice:** Never share Aadhaar/OTP publicly. Use only official portals.")
    
    st.stop()  # Stop execution here until language is selected


# ---------- Main Content (shown only after language selection) ----------
selected_language = st.session_state.selected_language
lang_code = st.session_state.lang_code

# Add back button in sidebar
with st.sidebar:
    st.title("🪪 Viveka - Aadhaar-DBT Awareness")
    st.caption(f"Language: {selected_language}")
    if st.button("← Change Language", use_container_width=True):
        st.session_state.selected_language = None
        st.session_state.lang_code = None
        st.rerun()
    
    st.divider()
    st.info(t("Never share Aadhaar/OTP publicly. Use only official portals.", lang_code))

# ---------- Main Title ----------
st.title(t("Aadhaar-linked vs DBT-enabled Aadhaar-seeded Bank Accounts", lang_code))

# ---------- Create Tabs for Different Sections ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    t("📖 Information", lang_code),
    t("🎯 Quiz", lang_code), 
    t("🎥 Video", lang_code),
    t("🔗 Resources", lang_code),
    t("📝 Feedback", lang_code)
])

# ---------- Tab 1: Information Section ----------
with tab1:
    # ---------- Explanations Section ----------
    with st.container():
        st.subheader(t("What is the difference?", lang_code))
        explanation_en = (
            "Aadhaar-linked bank account means your bank has linked your Aadhaar number for KYC or identification.\n\n"
            "DBT-enabled Aadhaar-seeded account means your Aadhaar is properly seeded and marked as 'DBT-enabled' in the NPCI mapper,"
            " so government Direct Benefit Transfer (DBT) payments can be credited to this account."
        )
        st.write(t(explanation_en, lang_code))

    # ---------- Steps Section ----------
    with st.container():
        st.subheader(t("Steps to check Aadhaar–bank mapping (NPCI Mapper)", lang_code))
        steps = [
            "Visit the official UIDAI/Bank Mapper service.",
            "Use your Aadhaar number and an OTP sent to your registered mobile.",
            "Confirm which bank account is mapped for DBT.",
            "If needed, visit your bank to seed/update Aadhaar for DBT.",
        ]
        for i, s_text in enumerate(steps, start=1):
            st.markdown(f"{i}. {t(s_text, lang_code)}")

    # ---------- Important Links ----------
    with st.container():
        st.subheader(t("Important Links", lang_code))
        
        # Common links for all languages
        common_links = {
            "UIDAI": "https://uidai.gov.in/",
            "DBT Bharat": "https://dbtbharat.gov.in/",
            "UIDAI Bank Mapper (mAadhaar info)": "https://uidai.gov.in/my-aadhaar/avail-aadhaar-services.html",
        }
        
        # State-specific links based on language
        state_links = {}
        if lang_code == "te":  # Telugu - Telangana
            state_links = {
                "Telangana ePASS": "https://telanganaepass.cgg.gov.in/",
            }
        elif lang_code == "kn":  # Kannada - Karnataka
            state_links = {
                "Karnataka SSP": "https://ssp.postmatric.karnataka.gov.in/",
            }
        elif lang_code == "mr":  # Marathi - Maharashtra
            state_links = {
                "Maharashtra DBT": "https://mahadbt.maharashtra.gov.in/login/login?utm_source=chatgpt.com",
            }
        elif lang_code in ["en", "hi"]:  # English and Hindi - show all state links
            state_links = {
                "Telangana ePASS": "https://telanganaepass.cgg.gov.in/",
                "Karnataka SSP": "https://ssp.postmatric.karnataka.gov.in/",
                "Maharashtra DBT": "https://mahadbt.maharashtra.gov.in/login/login?utm_source=chatgpt.com",
            }
        
        # Display common links
        for label, url in common_links.items():
            st.markdown(f"- [{t(label, lang_code)}]({url})")
        
        # Display state-specific links
        for label, url in state_links.items():
            st.markdown(f"- [{t(label, lang_code)}]({url})")

# ---------- Tab 2: Quiz Section ----------
with tab2:
    st.subheader(t("Quick Awareness Quiz", lang_code))
    quiz_questions = [
        {
            "q": "DBT-enabled Aadhaar-seeded account is required to receive government benefit payments.",
            "options": ["True", "False"],
            "answer": "True",
        },
        {
            "q": "Aadhaar-linked and DBT-enabled mean exactly the same thing.",
            "options": ["True", "False"],
            "answer": "False",
        },
        {
            "q": "Where is DBT enablement recorded for Aadhaar?",
            "options": [
                "At NPCI mapper",
                "Only on your ATM card",
                "Only at State scholarship portal",
            ],
            "answer": "At NPCI mapper",
        },
        {
            "q": "To check which bank is mapped for DBT, you should use:",
            "options": [
                "Any public forum",
                "Official UIDAI/Bank Mapper with OTP",
                "Random third-party app",
            ],
            "answer": "Official UIDAI/Bank Mapper with OTP",
        },
    ]

    for idx, q in enumerate(quiz_questions, start=1):
        st.markdown(f"**{t('Question', lang_code)} {idx}:** {t(q['q'], lang_code)}")
        choice = st.radio(
            t("Choose one", lang_code),
            [t(opt, lang_code) for opt in q["options"]],
            index=None,
            key=f"quiz_{idx}",
        )
        if choice is not None:
            is_correct = choice == t(q["answer"], lang_code)
            if is_correct:
                st.success(t("Correct!", lang_code))
            else:
                st.error(t("Incorrect.", lang_code))

# ---------- Tab 3: Video Section ----------
with tab3:
    if lang_code in ["hi", "te", "kn"]:
        st.subheader(t("Awareness Video", lang_code))
        st.caption(t("Replace this with your Canva-made explainer later.", lang_code))
        video_url = (
            "https://youtu.be/fcxkNDNYNkU?si=1ETDpl__HudiLliP" if lang_code == "hi" else
            "https://youtu.be/AafUd-LVxnA?si=jZS-g2A7Sf631LZN" if lang_code == "te" else
            "https://youtu.be/vs3uSLWX1ls?si=5c9EYF5wwf8N08JO"
        )
        st.video(video_url)
    else:
        st.subheader("Awareness Comic")
        try:
            image_path = (
                r"C:\Users\91967\Downloads\ChatGPT Image Sep 24, 2025, 11_30_51 PM.png" if lang_code == "mr" else
                r"C:\Users\91967\Downloads\ChatGPT Image Sep 24, 2025, 09_01_27 PM.png"
            )
            st.image(image_path, use_container_width=True)
        except Exception as e:
            st.error("Could not load image. Please verify the file path.")
            st.caption(str(e))

# ---------- Tab 4: Resources Section ----------
with tab4:
    st.subheader(t("Resources", lang_code))
    st.write(t("Official portals for information and services:", lang_code))
    
    # Display common links
    for label, url in common_links.items():
        st.markdown(f"- [{t(label, lang_code)}]({url})")
    
    # Display state-specific links
    for label, url in state_links.items():
        st.markdown(f"- [{t(label, lang_code)}]({url})")
    
    st.info(t("Never share Aadhaar/OTP publicly, use only official portals.", lang_code))

# ---------- Tab 5: Feedback Section ----------
with tab5:
    st.subheader(t("Feedback / Help Request", lang_code))
    with st.form("feedback_form", clear_on_submit=True):
        name = st.text_input(t("Name", lang_code))
        state = st.selectbox(
            t("State", lang_code),
            [t("Telangana", lang_code), t("Karnataka", lang_code), t("Other", lang_code)],
        )
        need_help = st.radio(t("Need Help?", lang_code), [t("Yes", lang_code), t("No", lang_code)])
        contact = st.text_input(t("Optional contact (phone/email)", lang_code))
        submitted = st.form_submit_button(t("Submit", lang_code))

    if submitted:
        # Store raw English equivalents for CSV consistency
        # Map back translated choices to English for CSV
        def back_to_en(value: str, choices_en: list[str]) -> str:
            for base in choices_en:
                if value == t(base, lang_code):
                    return base
            return value

        state_en = back_to_en(state, ["Telangana", "Karnataka", "Other"])
        need_help_en = back_to_en(need_help, ["Yes", "No"])

        row = {
            "timestamp": datetime.utcnow().isoformat(),
            "name": name,
            "state": state_en,
            "need_help": need_help_en,
            "contact": contact,
            "ui_language": selected_language,
        }

        csv_path = "feedback.csv"
        file_exists = os.path.exists(csv_path)

        try:
            df_new = pd.DataFrame([row])
            if file_exists:
                df_existing = pd.read_csv(csv_path)
                df_all = pd.concat([df_existing, df_new], ignore_index=True)
            else:
                df_all = df_new
            df_all.to_csv(csv_path, index=False)
            st.success(t("Thank you! Your response has been recorded.", lang_code))
        except Exception as e:
            st.error(t("Could not save feedback. Please try again.", lang_code))
            st.caption(str(e))

# ---------- Footer ----------
st.markdown("---")
st.caption(t("This is an awareness prototype for demonstration/education.", lang_code))

# ---------- Sanskrit Meaning Footer ----------
