from models import PaperState
from datetime import datetime
import os, time, re
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from Helpersfunctions.progress import append_progress
import tiktoken

load_dotenv()

# --- Helper: Tokenize and chunk text using tiktoken ---
def tokenize_and_chunk(text: str, max_chunk_tokens: int = 1800):
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = [enc.decode(tokens[i:i + max_chunk_tokens]) for i in range(0, len(tokens), max_chunk_tokens)]
    return chunks

# --- Helper: Safe Groq API invocation with retries ---
def safe_invoke(chat_groq, messages, retries: int = 2):
    for attempt in range(retries):
        try:
            response = chat_groq.invoke(messages)
            if hasattr(response, "content"):
                return response.content.strip()
            return str(response).strip()
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    return "⚠️ Error formatting this section."

def generate_report_node(state: PaperState) -> PaperState:
    """Generate a visually engaging Medium-style Markdown report using ChatGroq."""

    append_progress("🧾 Generating Medium-style research blog — please wait...")

    # Initialize Groq model for text styling
    chat_groq = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="groq/compound-mini"
    )

    title = getattr(state, "title", "Untitled Research Blog")
    author = "Sai Krish"

    # --- Header setup ---
    report_header = f"""# {title} ✨  
*By {author}*  
**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  

# ✨ ThinkScribe: From Research to Readability

"""

    enhanced_text = getattr(state, "text", "").strip()
    if not enhanced_text:
        state.report_file = "⚠️ No enhanced text available for report generation."
        append_progress("⚠️ No enhanced text found — skipping report generation.")
        return state

    # --- Tokenize and chunk using tiktoken ---
    chunks = tokenize_and_chunk(enhanced_text, max_chunk_tokens=1800)
    print(f"🧩 Splitting report generation into {len(chunks)} manageable sections.")
    append_progress(f"🧩 Report content split into {len(chunks)} chunks for formatting.")

    # --- System instructions ---
    system_message = (
        "You are a **professional Medium blog editor and Markdown stylist**.\n\n"
        "🎯 **Objective:**\n"
        "- Format the text into a **Medium-style Markdown blog** with clear sectioning, rhythm, and readability.\n"
        "- Focus purely on structure, formatting, and flow — do not alter the content.\n"
        "- Maintain all facts, tone, and order.\n\n"

        "🪶 **Style & Structure:**\n"
        "- Start with the title as `# {title}` (no emojis).\n"
        "- Use **bold** for key phrases and *italics* for subtle emphasis.\n"
        "- Use `##` and `###` for subheadings.\n"
        "- Break dense paragraphs into 2–3 sentence blocks for rhythm.\n"
        "- Use blockquotes (`>`) for insights or impactful sentences.\n"
        "- Keep spacing clean — two line breaks before major sections.\n"
        "- Maintain natural flow and paragraph pacing.\n\n"

        "🎨 **Formatting Rules:**\n"
        "- Do NOT reword, summarize, or add explanations.\n"
        "- Keep all technical terms and sentences unchanged.\n"
        "- Only adjust formatting for clarity and visual appeal.\n"
        "- If an image reference exists, style it as:\n"
        "  <p align='center'><img src='...' width='720px' height='420px' "
        "style='object-fit:cover; border-radius:12px; box-shadow:0 3px 8px rgba(0,0,0,0.2); margin:24px 0;'/></p>\n\n"

        "⚙️ **Output Policy:**\n"
        "- Return only the final Medium-style Markdown blog — no reasoning or meta text.\n"
        "- No '<think>' or analysis content.\n"
        "- The output must be clean, elegant Markdown — ready for Medium publication.\n"
    )

    formatted_sections = []

    # --- Process each chunk ---
    for idx, chunk in enumerate(chunks):
        print(f"🪶 Formatting chunk {idx + 1}/{len(chunks)}...")
        append_progress(f"🪶 Formatting chunk {idx + 1}/{len(chunks)}...")

        user_message = (
            f"Format the following text into a **Medium-style Markdown blog section**:\n\n"
            f"---\n{chunk}\n---\n\n"
            "Ensure structure, spacing, and readability are consistent with Medium's visual flow."
        )

        formatted_chunk = safe_invoke(chat_groq, [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ])
        formatted_sections.append(formatted_chunk)

    # --- Merge formatted chunks ---
    report_body = "\n\n".join(formatted_sections).strip()
    report_output = report_header + report_body

    # --- Clean duplicated headers / excessive spacing ---
    report_output = re.sub(r"(#+\s.*?)(\n#+\s.*?)", r"\1\n\n", report_output)
    report_output = re.sub(r"\n{3,}", "\n\n", report_output)

    # --- Save report ---
    os.makedirs("Generated_Reports", exist_ok=True)
    report_path = "Generated_Reports/AI_Paper_Report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_output)

    state.report = report_output
    state.report_file = report_path

    print(f"✅ Medium-style Markdown report saved successfully → {report_path}")
    append_progress(f"✅ Report saved successfully to {report_path}")

    return state
