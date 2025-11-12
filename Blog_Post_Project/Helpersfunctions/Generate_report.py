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

    report = f"#✨ ThinkScribe: From Research to Readability\n\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    title = state.title
    enhanced_text = state.text
    #feedback = state.last_feedback

    if not enhanced_text:
        state.report_file = "No enhanced text available to generate report."
        append_progress("⚠️ No enhanced text available for report generation")
        return state

    # Show we're starting report generation
    append_progress("Generating LinkedIn-style report with LLM")

    # ---------------- SYSTEM MESSAGE ----------------
    system_message = (
        "You are a creative social media editor and Markdown stylist who crafts story-driven "
        "LinkedIn posts from technical content.\n\n"
        "🎯 Objective:\n"
        "- Transform the given text into a **beautiful LinkedIn-style Markdown post**.\n"
        "- Keep all facts, logic, and sequence **exactly the same** — no paraphrasing or rewriting.\n"
        "- Focus entirely on **structure, rhythm, formatting, and emotional flow**.\n\n"
        "🪶 Tone:\n"
        "- Conversational, engaging, and reflective — like a professional sharing a learning journey.\n"
        "- Blend storytelling with insight; keep a natural human rhythm.\n"
        "- Avoid overly academic phrasing — sound clear and authentic.\n\n"
        "🎨 Formatting Style:\n"
        "- Use `# {title}` as the headline — include **one fitting emoji**.\n"
        "- Use short paragraphs (1–3 sentences max) for rhythm.\n"
        "- Add emojis that match the emotion or flow (✨💡🚀🔥💭➡️📊🧠🙌 etc.).\n"
        "- Highlight key ideas using **bold**, *italics*, and `>` blockquotes.\n"
        "- Use bullet points (•) or numbered steps (1️⃣ 2️⃣ 3️⃣) for clarity where needed.\n"
        "- Use color hints with emojis (🟢🔵🟣🟠) to segment sections visually.\n"
        "- End the post with a short **reflective takeaway or call-to-thought** — "
        "something that fits LinkedIn’s professional tone (💬🤔🙌).\n\n"
        "⚠️ Rules:\n"
        "- Do **not** add new ideas, summaries, or conclusions.\n"
        "- Do **not** alter any original meaning.\n"
        "- Maintain the natural storytelling flow while enhancing readability and emotion.\n"
        "- Return **only** the final styled Markdown — no notes, explanations, or metadata."
    )

    # ---------------- USER MESSAGE ----------------
    user_message = (
        f"Here is the content to format:\n\n"
        f"Title: {title}\n\n"
        f"Content:\n{enhanced_text}\n\n"
        "Now format this content into a **LinkedIn-style Markdown post** "
        "that looks visually appealing, easy to read, and emotionally engaging. "
        "Keep the tone conversational, with natural breaks, emojis, and clear rhythm."
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
