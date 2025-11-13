from models import PaperState
from datetime import datetime
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from Helpersfunctions.progress import append_progress
load_dotenv()

#os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")

def generate_report_node(state: PaperState) -> PaperState:
    """Generate a visually engaging LinkedIn-style Markdown report using ChatGroq."""

    chat_groq = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="moonshotai/kimi-k2-instruct-0905")
    title = getattr(state, 'title', '')
    title_add = f'''# {title} ✨  
*By Sai Krish* \n'''
    report = title_add + f"#✨ ThinkScribe: From Research to Readability\n\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    enhanced_text = getattr(state, 'text', '')
    #feedback = state.last_feedback

    if not enhanced_text:
        state.report_file = "No enhanced text available to generate report."
        append_progress("⚠️ No enhanced text available for report generation")
        return state

    # Show we're starting report generation
    append_progress("Generating LinkedIn-style report with LLM using the styling agent")

    # ---------------- SYSTEM MESSAGE ----------------
    system_message = (
        "You are a professional **Medium blog editor and stylist**. "
        "Your job is to make a technical article look like a clean, well-structured Medium post.\n\n"
        "🎯 **Objective:**\n"
        "- Format the content into a **Medium-style Markdown blog**.\n"
        "- Focus purely on **readability**, **visual flow**, and **section rhythm**.\n"
        "- Do NOT alter, summarize, or add new content.\n"
        "- Keep all sentences, ideas, and order identical.\n\n"
        "🖋️ **Tone and Structure Guidelines:**\n"
        "- Write like a thoughtful explainer: smooth transitions, gentle pacing, clear hierarchy.\n"
        "- Break dense paragraphs into 2–3 sentence blocks for rhythm.\n"
        "- Use clean Markdown headings (`##`, `###`) for logical sections.\n"
        "- Maintain a professional but accessible tone — clear, reflective, and narrative.\n\n"
        "🎨 **Styling Rules:**\n"
        "- Begin with `# {title}` — no emojis in the title.\n"
        "- Add a short introductory paragraph if already present (do not invent one).\n"
        "- Use **bold** and *italics* for emphasis on key ideas.\n"
        "- Use blockquotes (`>`) for key insights, comparisons, or reflective statements.\n"
        "- Maintain spacing between major sections (two line breaks before new headers).\n"
        "- For embedded visuals, enforce consistent size and centering:\n"
        "  <p align='center'><img src='...' width='720px' height='420px' "
        "style='object-fit:cover; border-radius:12px; box-shadow:0 3px 8px rgba(0,0,0,0.2); margin:24px 0;'/></p>\n"
        "- Avoid emoji clutter — only keep if they’re already present and contextually meaningful.\n"
        "- End the post gracefully with a closing thought already within the text (no new lines).\n\n"
        "⚠️ **Rules:**\n"
        "- Do NOT rephrase or add content.\n"
        "- Do NOT include any explanations or metadata.\n"
        "- Return only the final Medium-style Markdown text."
        "⚠️ STRICT OUTPUT RULES:\n"
"- Never include reasoning, analysis, or thought process.\n"
"- No '<think>' or 'analysis' text.\n"
"- Return only the final, polished Markdown blog post — ready for publication.\n"
"- The output must look like a cohesive Medium-style article, not a model response."
    )

    # --------------- USER PROMPT ---------------
    user_message = (
        f"Here is the content to format as a Medium-style blog post:\n\n"
        f"Title: {title}\n\n"
        f"Content:\n{enhanced_text}\n\n"
        "Now format this text into a **Medium-style Markdown post** that looks professional, "
        "easy to read, and visually elegant — while keeping all wording and sequence intact."
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    try:
        response = chat_groq.invoke(messages)
        report_output = response.content.strip() if hasattr(response, "content") else str(response).strip()
    except Exception as e:
        report_output = f"Error generating LinkedIn-style report with ChatGroq: {e}"
        print(f"Error generating LinkedIn-style report with ChatGroq: {e}")
        append_progress(f"Error generating LinkedIn-style report with ChatGroq: {e}")

    # Combine and save
    report += report_output
    report_name = f"Generated_Reports/AI_Paper_Report.md"

    os.makedirs("Generated_Reports", exist_ok=True)
    with open(report_name, "w", encoding="utf-8") as f:
        f.write(report)

    state.report = report

    state.report_file = report_name
    print(f"✅ LinkedIn-style Markdown report saved as: {report_name}")
    append_progress(f"✅ Saved report to {report_name}")
    return state
