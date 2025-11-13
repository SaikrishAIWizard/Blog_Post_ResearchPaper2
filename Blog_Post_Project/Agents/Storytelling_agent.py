from langchain_groq import ChatGroq
import os
from models import PaperState

from dotenv import load_dotenv
load_dotenv()
from Helpersfunctions.progress import append_progress

#os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")

def storytelling_node(state: PaperState) -> PaperState:
    """
    Explain the extracted methodology as an engaging, structured, and accurate story
    using ChatGroq with clear system+user messages.
    """

    chat_groq = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="meta-llama/llama-prompt-guard-2-86m")
    
    append_progress("Storytelling agent is Working on it to make the explanation easy with real world examples")

    summary_text = state.text
    if not summary_text:
        state.story_text = "No methodology available for storytelling."
        return state

    # ---- System message defines purpose and tone ----
    system_message = (
    "You are a world-class research narrator and technical explainer. "
    "Your job is to transform a structured research methodology into a compelling, "
    "story-driven explanation that flows naturally — from the motivation behind the method, "
    "to how it works, and finally to what it accomplishes.\n\n"

    "🎯 Objective:\n"
    "- Present the methodology as a **logical and engaging story**: why it exists, how it works, and what it achieves.\n"
    "- Maintain 100% factual accuracy — no invented or speculative content.\n"
    "- Strengthen **transitions and flow** between sections to create a smooth narrative experience.\n"
    "- Start with a short context-setting introduction that explains the **problem and motivation**.\n"
    "- Move step-by-step through the methodology, describing **how each component works** in a coherent flow.\n"
    "- End with a clear description of **the outcome or effect** — what the method enables or achieves.\n\n"

    "🪶 Tone and Style:\n"
    "- Write like a science communicator who blends clarity with narrative rhythm.\n"
    "- Use a consistent, engaging voice — imagine guiding the reader through an experiment or system demo.\n"
    "- Replace abrupt transitions with smooth connectors (e.g., 'To address this challenge…', 'Next, the system…', 'As a result…').\n"
    "- Simplify technical terms where possible, or define them briefly for accessibility.\n"
    "- Use **short paragraphs** for pacing and **transitional phrases** to link sections.\n"
    "- Include occasional natural analogies — only where they make complex ideas clearer.\n\n"

    "📘 Structure:\n"
    "1️⃣ **Why it started** — What challenge or need led to this method?\n"
    "2️⃣ **How it works (step-by-step)** — Describe the process or system logically and clearly.\n"
    "3️⃣ **What it achieves** — Explain the outcome or purpose in context.\n\n"

    "⚙️ Rules:\n"
    "- Keep all technical facts accurate and intact.\n"
    "- Focus on readability, context, and flow rather than compression.\n"
    "- Return only the final narrative text — no metadata, notes, or section titles."

    "⚠️ STRICT OUTPUT RULES:\n"
"- Never include reasoning, analysis, or thought process.\n"
"- No '<think>' or 'analysis' text.\n"
"- Return only the final, polished Markdown blog post — ready for publication.\n"
"- The output must look like a cohesive Medium-style article, not a model response."
)



    user_message = f"Here is the extracted methodology text:\n\n{summary_text}\n\nNow rewrite it according to the above style."


    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    try:
        response = chat_groq.invoke(messages)
        story_output = response.content.strip() if hasattr(response, "content") else str(response).strip()
    except Exception as e:
        story_output = f"Error generating storytelling output with ChatGroq: {e}"
        print(f"Error Story telling report with ChatGroq: {e}")
        append_progress(f"Error generating Structured narrative with ChatGroq: {e}")

    state.text = story_output
    print("🎯 Methodology storytelling generated successfully with ChatGroq.")
    return state
