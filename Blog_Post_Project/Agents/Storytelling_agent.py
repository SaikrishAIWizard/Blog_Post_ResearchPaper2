from langchain_groq import ChatGroq
import os, time, tiktoken
from models import PaperState
from dotenv import load_dotenv
from Helpersfunctions.progress import append_progress
import re

load_dotenv()

def storytelling_node(state: PaperState) -> PaperState:
    """
    Converts the structured methodology into an engaging, story-style narrative
    while maintaining technical accuracy and smooth flow. 
    Uses token-based chunking and feedback refinement.
    """

    # ✅ Use Groq’s high-context reasoning model
    chat_groq = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="openai/gpt-oss-20b")

    append_progress("🧠 Storytelling agent is crafting a structured, human-like explanation... Please wait...")

    summary_text = state.text.strip() if state.text else ""
    feedback = getattr(state, "reader_feedback", "").strip()

    if not summary_text:
        state.story_text = "⚠️ No methodology available for storytelling."
        return state

    # --- Use tiktoken for chunking (no Hugging Face needed) ---
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(summary_text)
    max_chunk_tokens = 2500  # safe range for qwen/llama context
    chunks = [enc.decode(tokens[i:i + max_chunk_tokens]) for i in range(0, len(tokens), max_chunk_tokens)]

    print(f"🧩 Split methodology into {len(chunks)} storytelling chunks.")
    append_progress(f"🧩 Split methodology into {len(chunks)} chunks for storytelling...")

    # --- System message defines tone and structure ---
    system_message = (
        "You are a world-class research narrator and technical explainer.\n\n"
        "Your task: Convert a structured research methodology into a **story-driven explanation** "
        "that flows naturally from the motivation behind the research, to how it works, and what it achieves.\n\n"

        "🎯 **Objectives:**\n"
        "- Transform the technical methodology into a narrative that explains **why it started**, **how it works**, and **what it achieves**.\n"
        "- Maintain 100% factual accuracy — no speculation.\n"
        "- Strengthen transitions and flow between sections.\n"
        "- Incorporate reviewer feedback when available to refine structure and engagement.\n\n"

        "🪶 **Tone & Style:**\n"
        "- Write like a science storyteller guiding readers through an experiment.\n"
        "- Use smooth transitions (e.g., 'To address this challenge…', 'Next, the system…', 'As a result…').\n"
        "- Prefer clear, short paragraphs and natural pacing.\n"
        "- Add light analogies or relatable phrasing only if it enhances clarity.\n\n"

        "📘 **Narrative Structure:**\n"
        "1️⃣ Why it started — what challenge led to this method?\n"
        "2️⃣ How it works — step-by-step explanation of the process or system.\n"
        "3️⃣ What it achieves — the key outcome or benefit.\n\n"

        "⚙️ **Output Rules:**\n"
        "- Keep all technical facts intact.\n"
        "- No reasoning, explanations, or <think> text.\n"
        "- Return only the final, polished Markdown narrative, ready for Medium-style publication.\n"
    )

    story_parts = []

    # --- Safe invoke with retries ---
    def safe_invoke(messages, retries=2):
        for attempt in range(retries):
            try:
                response = chat_groq.invoke(messages)
                if hasattr(response, "content"):
                    return response.content.strip()
                return str(response).strip()
            except Exception as e:
                print(f"⚠️ Attempt {attempt + 1} failed: {e}")
                time.sleep(2)
        return "⚠️ Error generating this section."

    # --- Process chunks sequentially ---
    for idx, chunk in enumerate(chunks):
        print(f"✍️ Generating storytelling section {idx + 1}/{len(chunks)}...")
        append_progress(f"✍️ Generating storytelling section {idx + 1}/{len(chunks)}...")

        user_message = (
            f"Here is part {idx + 1} of the extracted methodology text:\n\n"
            f"---\n{chunk}\n---\n\n"
            "Rewrite this part into an engaging, factual, story-driven explanation following the structure above."
        )

        # Add feedback context only to the first chunk
        if feedback and idx == 0:
            user_message += f"\n\nReviewer feedback to incorporate:\n{feedback}\n"

        story_part = safe_invoke([
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ])

        story_parts.append(story_part)

    # --- Merge and clean final story ---
    full_story = "\n\n".join(story_parts).strip()

    # Remove accidental duplicate sections or repeated headers
    full_story = re.sub(r'(#+.*?)(\n\s*#+.*?)+', r'\1', full_story, flags=re.S)

    # --- Save outputs ---
    state.story_text = full_story
    state.text = full_story

    print("🎯 Storytelling generation complete — output is reader-ready.")
    append_progress("✅ Storytelling generation complete.")

    return state
