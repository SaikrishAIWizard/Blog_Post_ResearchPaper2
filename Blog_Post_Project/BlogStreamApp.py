import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
from Agent_workflow import graph
import time
import threading
from Helpersfunctions.progress import clear as clear_progress, get_messages, append_progress, set_result, get_result
from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from dotenv import load_dotenv
load_dotenv()

import os
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"


# ============ PAGE CONFIGURATION ============
st.set_page_config(
    page_title="📰 Research Paper Blog Post Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============ CUSTOM CSS ============
st.markdown("""
<style>
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .header-title {
        text-align: center;
        color: #1a73e8;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .header-subtitle {
        text-align: center;
        color: #5f6368;
        font-size: 1rem;
        margin-bottom: 30px;
    }
    .input-section {
        background: white;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .results-section {
        background: white;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        margin: 10px 0;
    }
    .success-box {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #1a5f3f;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .warning-box {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: #5f3f1a;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# ============ HELPER FUNCTIONS ============
def load_report_from_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error loading report: {e}"


def format_duration(seconds):
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"


def get_state_value(state, key, default=None):
    if isinstance(state, dict):
        return state.get(key, default)
    else:
        return getattr(state, key, default)


def serialize_state_to_dict(state):
    state_dict = {}
    try:
        if isinstance(state, dict):
            for key, val in state.items():
                if isinstance(val, (str, int, float, bool)) or val is None:
                    state_dict[key] = val
                else:
                    state_dict[key] = str(val)[:1000]
        else:
            for attr in dir(state):
                if not attr.startswith("_"):
                    val = getattr(state, attr)
                    if isinstance(val, (str, int, float, bool)) or val is None:
                        state_dict[attr] = val
                    else:
                        state_dict[attr] = str(val)[:1000]
    except Exception as e:
        state_dict["error"] = str(e)
    return state_dict

import smtplib
from email.message import EmailMessage


from xhtml2pdf import pisa
import markdown
from io import BytesIO

def generate_pdf_from_markdown(md_text):
    # Convert Markdown → HTML
    html = markdown.markdown(md_text)

    # Add simple styling
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Helvetica, Arial, sans-serif;
                padding: 20px;
                font-size: 12pt;
            }}
            h1, h2, h3 {{
                color: #003366;
            }}
            pre {{
                background: #f4f4f4;
                padding: 10px;
                border-radius: 5px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            table, th, td {{
                border: 1px solid black;
                padding: 6px;
            }}
        </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """

    buffer = BytesIO()
    pisa.CreatePDF(html, dest=buffer)

    buffer.seek(0)
    return buffer.read()


def send_email_report(to_email, subject, body, attachment_content=None, attachment_name=None):
    try:
        sender_email = "vijayasatya369@gmail.com"  # change this
        sender_password = os.getenv("EMAIL_APP_PASSWORD")  # set via environment variable for safety

        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        if attachment_content and attachment_name:

            # 1️⃣ Generate real PDF bytes
            pdf_bytes = generate_pdf_from_markdown(attachment_content)

            msg.add_attachment(
                pdf_bytes,
                maintype="application",
                subtype="pdf",
                filename=attachment_name + ".pdf"
            )

            # 2️⃣ Attach Markdown text
            msg.add_attachment(
                attachment_content.encode("utf-8"),
                maintype="text",
                subtype="markdown",
                filename=attachment_name + ".md"
            )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True, "✅ Email sent successfully!"
    except Exception as e:
        return False, f"❌ Failed to send email: {e}"



# ============ INITIAL STATE ============
if 'final_state' not in st.session_state:
    st.session_state.final_state = None
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False
if 'execution_time' not in st.session_state:
    st.session_state.execution_time = 0


# ============ HEADER ============
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<div class='header-title'>📰 Research Paper Blog Post Generator</div>", unsafe_allow_html=True)
    st.markdown("<div class='header-subtitle'>Transform academic papers into engaging blog posts using AI agents</div>", unsafe_allow_html=True)
st.divider()


# ============ SIDEBAR ============
from pathlib import Path
import os
import streamlit as st
from groq import Groq

with st.sidebar:
    st.header("⚙️ Configuration")

    # --- 🔑 Groq API Key Input ---
    st.subheader("🔑 Groq API Configuration")

    # Preserve key between reruns (session only)
    if "groq_key" not in st.session_state:
        st.session_state.groq_key = ""

    groq_input = st.text_input(
        "Enter your Groq API Key",
        type="password",
        value=st.session_state.groq_key,
        placeholder="gsk_********************************",
    )

    if groq_input:
        st.session_state.groq_key = groq_input
        os.environ["GROQ_API_KEY"] = groq_input
        try:
            client = Groq(api_key=groq_input)
            # quick ping to check if valid
            st.success("✅ Groq key loaded successfully!")
        except Exception as e:
            st.warning(f"⚠️ Invalid or inactive API key: {e}")
    else:
        st.info("Please enter your Groq API key to enable blog generation.")

    st.markdown(
    """
    <a href="https://console.groq.com/keys" target="_blank">
        <button style="
            background-color:#4CAF50;
            color:white;
            padding:8px 16px;
            border:none;
            border-radius:6px;
            cursor:pointer;
        ">🔑 Get Groq API Key</button>
    </a>
    """,
    unsafe_allow_html=True
)


    st.divider()

    # --- 🔁 Recursion Limit / Max Iterations ---
    recursion_limit = st.slider("Max iterations", 5, 50, 25)

    st.divider()

    # --- ℹ️ Project Information ---
    st.subheader("📂 Project Info")
    st.info(
        """
        **Project:** Blog Post Generator  
        **Framework:** LangGraph + LangChain  
        **LLM:** Groq (Meta-Llama)
        """
    )

    st.divider()

    # --- 📚 Generated Reports Section ---
    reports_dir = Path("Generated_Reports")
    st.subheader("📚 Generated Reports")

    if reports_dir.exists():
        files = sorted(reports_dir.glob("*.md"), reverse=True)
        if files:
            st.write(f"Total reports: {len(files)}")
            for file in files[:5]:  # show latest 5 reports
                st.markdown(f"- 📄 [{file.name}]({file.as_posix()})")
        else:
            st.write("No reports yet.")
    else:
        st.write("Reports directory not found.")

# ============ INPUT ============
st.markdown("<div class='input-section'>", unsafe_allow_html=True)
st.subheader("📋 Input Research Paper")
col1, col2 = st.columns(2)
with col1:
    input_type = st.radio("Input Type", ["ArXiv ID", "Research Topic"], horizontal=True)
with col2:
    user_input = st.text_input("Enter Value", placeholder="e.g., 2005.11401 or Attention Mechanisms")
    #st.divider()
    # --- 📧 Email Configuration ---
    #st.subheader("📧 Report Delivery")
    email_id = st.text_input("Enter your email to receive the report", placeholder="example@email.com")
st.markdown("</div>", unsafe_allow_html=True)


# ============ ACTION BUTTONS ============
st.markdown("<div class='input-section'>", unsafe_allow_html=True)
col1, col2 = st.columns([2, 1])
run_button = col1.button(
    "🚀 Generate Blog Post",
    use_container_width=True,
    disabled=not user_input or st.session_state.is_processing or "GROQ_API_KEY" not in os.environ or not email_id
)

col2.button("💾 Download", use_container_width=True, disabled=st.session_state.final_state is None)
st.markdown("</div>", unsafe_allow_html=True)


# ============ MAIN EXECUTION ============
if run_button and user_input:
    st.session_state.is_processing = True

    progress_placeholder = st.empty()
    messages_placeholder = st.empty()
    progress_bar = progress_placeholder.progress(0)

    try:
        clear_progress()
    except Exception:
        pass

    workflow_done = threading.Event()
    workflow_error = {"error": None}
    workflow_result = {"final_state": None}
    start_time = time.time()

    # ---- Background thread (no Streamlit calls) ----
    def run_workflow():
        try:
            append_progress("⏳ Started processing research paper")
            result = graph.invoke({"research_paper": user_input}, config={"recursion_limit": recursion_limit})
            workflow_result["final_state"] = result
            append_progress("✅ Workflow finished successfully")
        except Exception as e:
            workflow_error["error"] = str(e)
            append_progress(f"❌ Error during workflow: {e}")
        finally:
            workflow_done.set()

    thread = threading.Thread(target=run_workflow)
    thread.start()

    with st.spinner("🔄 Generating blog post..."):
        progress = 0
        while not workflow_done.is_set():
            msgs = get_messages()
            if msgs:
                md = "\n".join(f"- {m}" for m in msgs) if isinstance(msgs, list) else str(msgs)
                messages_placeholder.markdown(md)
                progress = min(100, len(msgs) * 8)
                progress_bar.progress(progress)
            time.sleep(1)

        # Final refresh
        msgs = get_messages()
        if msgs:
            md = "\n".join(f"- {m}" for m in msgs) if isinstance(msgs, list) else str(msgs)
            messages_placeholder.markdown(md)
        progress_bar.progress(100)

    # ---- Update session state safely (main thread) ----
    if workflow_error["error"]:
        st.markdown(f"<div class='warning-box'>❌ Error: {workflow_error['error']}</div>", unsafe_allow_html=True)
        st.session_state.final_state = None
    else:
        st.session_state.final_state = workflow_result["final_state"]
        st.session_state.execution_time = time.time() - start_time
        st.markdown(f"<div class='success-box'>✅ Blog post generated successfully in {format_duration(st.session_state.execution_time)}!</div>", unsafe_allow_html=True)
                # --- Send email if provided ---
        if email_id:
            report_text = st.session_state.final_state.get("report")
            if report_text:
                attachment_name = f"blog_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                success, msg = send_email_report(
                    to_email=email_id,
                    subject="📰 Your AI-Generated Research Blog Report",
                    body=f"Hi there,\n\nYour requested research blog report is attached.\n\nGenerated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nBest,\nAI Blog Agent 🤖",
                    attachment_content=report_text,
                    attachment_name=attachment_name
                )
                if success:
                    st.markdown(f"<div class='success-box'>{msg}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='warning-box'>{msg}</div>", unsafe_allow_html=True)
            else:
                st.warning("Report generated but no text found to send via email.")


    st.session_state.is_processing = False
    st.rerun()


# ============ RESULTS SECTION ============
if st.session_state.final_state:
    st.divider()
    st.markdown("<div class='results-section'>", unsafe_allow_html=True)
    st.subheader("📊 Results & Analytics")

    state = st.session_state.final_state
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-box'><div>Processing Time</div><div style='font-size:1.5rem'>{format_duration(st.session_state.execution_time)}</div></div>", unsafe_allow_html=True)
    with col2:
        rating = get_state_value(state, 'reader_rating', 'N/A')
        st.markdown(f"<div class='metric-box'><div>Final Rating</div><div style='font-size:1.5rem'>⭐ {rating}</div></div>", unsafe_allow_html=True)
    with col3:
        loop_count = get_state_value(state, 'loop_count', 0)
        st.markdown(f"<div class='metric-box'><div>Iterations</div><div style='font-size:1.5rem'>🔄 {loop_count}</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-box'><div>Status</div><div style='font-size:1.5rem'>✅ Done</div></div>", unsafe_allow_html=True)

    st.divider()
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 Blog Post", "📝 Feedback", "🔍 Metadata", "💾 State", "📥 Download"])

    with tab1:
        st.subheader("Generated Blog Post")
        #report_content = None
        # report_file = get_state_value(state, 'report_file')
        # if report_file and os.path.exists(report_file):
        #     report_content = load_report_from_file(report_file)
        #if not report_content:
        report_content = get_state_value(state, 'report') or get_state_value(state, 'text')
        if report_content:
            st.markdown(report_content)
        else:
            st.warning("No report content found.")

    with tab2:
        st.subheader("Feedback")
        st.write(get_state_value(state, 'last_feedback', 'No feedback found'))

    with tab3:
        st.subheader("Metadata")
        st.text(get_state_value(state, 'title', 'Not extracted'))
        st.text(get_state_value(state, 'domain_expert', 'Unknown'))
        st.text(get_state_value(state, 'research_paper', 'Unknown'))
        
    with tab4:
        st.json(serialize_state_to_dict(state))

    with tab5:
        st.subheader("📥 Download Files")

        # --- JSON download (always works) ---
        state_json = json.dumps(serialize_state_to_dict(state), ensure_ascii=False, indent=2)
        file_name = f"state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        st.download_button(
            label="💾 Download State JSON",
            data=state_json.encode('utf-8'),
            file_name=file_name,
            mime="application/json",
            use_container_width=True
        )

        # --- Try all possible sources for the blog report ---
        report_text = None

        # 1️⃣ File on disk
        report_file = get_state_value(state, 'report_file')
        if report_file and os.path.exists(report_file):
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_text = f.read()
            except Exception as e:
                st.warning(f"Couldn't read report file: {e}")

        # 2️⃣ Text stored directly in state
        if not report_text:
            report_text = (
                get_state_value(state, 'report')
                or get_state_value(state, 'story_text')
                or get_state_value(state, 'enhanced_text')
            )

        # 3️⃣ Fallback if nothing found
        if not report_text:
            report_text = "No blog report text available."

        # --- Markdown report download ---
        st.download_button(
            label="📰 Download Blog Report (.md)",
            data=report_text.encode('utf-8'),
            file_name=f"blog_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )


    st.markdown("</div>", unsafe_allow_html=True)


# ============ FOOTER ============
st.divider()
col1, col2, col3 = st.columns(3)
with col2:
    st.caption("Built with ❤️ using Streamlit & LangGraph | © 2025")
