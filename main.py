import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time

# --- Page Config ---
st.set_page_config(
    page_title="Regulatory Report AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.warning("Google API Key not found. Please set GOOGLE_API_KEY in your .env file.")

# --- Logic Functions ---
def call_gemini_with_retry(prompt, model_name='gemini-flash-latest', is_text=True):
    model = genai.GenerativeModel(model_name)
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            return response.text.strip() if is_text else response
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                time.sleep(10)
                continue
            raise e

def identify_report(df):
    if not api_key: return "Unknown"
    headers = df.columns.tolist()
    sample = df.head(5).to_string()
    prompt = f"Identify this financial report type based on headers: {headers} and sample: {sample}. Return only the type name."
    try:
        return call_gemini_with_retry(prompt)
    except:
        return "Regulatory Report"

def get_ai_suggestions(df, report_type):
    if not api_key: return "API key missing."
    stats = df.describe(include='all').to_string()
    sample = df.head(10).to_string()
    prompt = f"As a regulatory expert, analyze this {report_type}. Stats: {stats}. Sample: {sample}. Provide: 1. Summary, 2. Risks/Anomalies, 3. Actions. Use Markdown."
    try:
        return call_gemini_with_retry(prompt)
    except Exception as e:
        return f"Error: {str(e)}"

# --- State Management ---
if 'df' not in st.session_state:
    st.session_state.df = None
if 'report_type' not in st.session_state:
    st.session_state.report_type = None

# --- CSS FOR HIGH-CONTRAST DASHBOARD ---
st.markdown("""
    <style>
    /* Global Background */
    .stApp {
        background-color: #f1f5f9 !important;
    }

    /* 1. FORCE DARK TEXT IN MAIN AREA - Target everything */
    [data-testid="stAppViewBlockContainer"], 
    [data-testid="stAppViewBlockContainer"] * {
        color: #0f172a !important;
    }

    /* 2. SIDEBAR STYLING - DARK THEME */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important; /* Darkest Navy */
        border-right: 1px solid #334155;
    }

    /* 3. FORCE LIGHT TEXT IN SIDEBAR - Target everything */
    [data-testid="stSidebar"], 
    [data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    /* 4. SPECIAL HANDLING FOR FILE UPLOADER IN SIDEBAR */
    [data-testid="stFileUploadDropzone"] {
        background-color: #1e293b !important; /* Stand out from the sidebar */
        border: 2px dashed #475569 !important;
        padding: 20px !important;
        border-radius: 12px !important;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #6366f1 !important;
        background-color: #2d3748 !important;
    }
    
    /* Force all labels, small text, and instructions to be bright white */
    [data-testid="stFileUploadDropzone"] p,
    [data-testid="stFileUploadDropzone"] small,
    [data-testid="stFileUploadDropzone"] span,
    [data-testid="stFileUploadDropzone"] div {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    /* Style the "Browse files" button specifically */
    [data-testid="stFileUploadDropzone"] button {
        background-color: #6366f1 !important;
        color: white !important;
        border: none !important;
        padding: 8px 16px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        margin-top: 10px !important;
    }

    /* 5. NAVIGATION BARS IN SIDEBAR */
    div.row-widget.stRadio > div[role="radiogroup"] > label {
        background-color: rgba(255, 255, 255, 0.05) !important;
        padding: 16px 20px !important;
        margin-bottom: 12px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex !important;
        align-items: center;
        width: 100% !important;
    }

    div.row-widget.stRadio > div[role="radiogroup"] > label:hover {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-color: #6366f1 !important;
    }

    div.row-widget.stRadio > div[role="radiogroup"] > label[data-selected="true"] {
        background-color: #6366f1 !important;
        border-color: #6366f1 !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }

    div.row-widget.stRadio > div[role="radiogroup"] > label[data-selected="true"] * {
        color: white !important;
        font-weight: 700 !important;
    }

    /* Hide radio circle */
    div.row-widget.stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] div:first-child {
        display: none !important;
    }

    /* 5. CONTENT CARDS */
    .content-card {
        background-color: #ffffff !important;
        padding: 2.5rem !important;
        border-radius: 20px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 2rem !important;
    }
    
    /* Ensure text INSIDE content-card is also dark */
    .content-card * {
        color: #0f172a !important;
    }

    /* 6. BADGE STYLING */
    .badge {
        background-color: #e0e7ff !important;
        color: #4338ca !important;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.8rem;
        text-transform: uppercase;
        border: 1px solid #c7d2fe;
    }

    /* 7. PRIMARY BUTTON */
    .stButton > button {
        background-color: #6366f1 !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📊 Control Panel")
    
    if st.session_state.df is not None:
        if st.button("➕ Import New Report"):
            st.session_state.df = None
            st.session_state.report_type = None
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### CATEGORIES")
        page = st.radio(
            "Nav",
            ["📄 Data Preview", "📊 Summary Stats", "💡 AI Analysis"],
            index=0,
            label_visibility="collapsed"
        )
    else:
        st.markdown("##### DATA SOURCE")
        uploaded_file = st.file_uploader("Upload CSV/Excel", type=['csv', 'xlsx'], label_visibility="collapsed")
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    st.session_state.df = pd.read_csv(uploaded_file)
                else:
                    st.session_state.df = pd.read_excel(uploaded_file)
                with st.spinner("Processing..."):
                    st.session_state.report_type = identify_report(st.session_state.df)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
        page = None

# --- Main Area ---

# Custom Header
col1, col2 = st.columns([1, 9])
with col1:
    try:
        st.image("logo.png", width=60)
    except:
        st.markdown("<h1 style='margin:0;'>📊</h1>", unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <h1 style='margin:0; font-size: 2rem;'>Regulatory Report AI</h1>
            {f'<span class="badge">{st.session_state.report_type}</span>' if st.session_state.report_type else ''}
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Content Rendering
if st.session_state.df is not None:
    df = st.session_state.df
    
    if page == "📄 Data Preview":
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.markdown("### Raw Data Insights")
        st.markdown("View and explore the uploaded dataset details below.")
        st.dataframe(df, use_container_width=True, height=500)
        st.markdown("</div>", unsafe_allow_html=True)
        
    elif page == "📊 Summary Stats":
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.markdown("### Statistical Summary")
        st.markdown("Automatic distribution and summary of all financial fields.")
        st.write(df.describe(include='all'))
        st.markdown("</div>", unsafe_allow_html=True)
        
    elif page == "💡 AI Analysis":
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.markdown("### Compliance Intelligence")
        st.markdown("Generate AI-driven risk assessments and regulatory suggestions.")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Analyze Report"):
            with st.spinner("Gemini is analyzing compliance patterns..."):
                suggestions = get_ai_suggestions(df, st.session_state.report_type)
                st.markdown(suggestions)
        else:
            st.info("System ready. Click the button above to start the AI evaluation.")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # Landing View
    st.markdown("<div class='content-card' style='text-align:center; padding: 5rem 2rem;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 3rem;'>Welcome to Regulatory AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.2rem; color: #64748b !important;'>Transforming financial data into regulatory intelligence.</p>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 📥 1. Upload")
        st.write("Securely import ORX or financial loss data.")
    with c2:
        st.markdown("### 🔍 2. Identify")
        st.write("AI identifies headers and report schemas.")
    with c3:
        st.markdown("### ⚡ 3. Resolve")
        st.write("Get actionable compliance suggestions.")
    st.markdown("</div>", unsafe_allow_html=True)
