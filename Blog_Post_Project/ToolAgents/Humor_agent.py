from langchain_groq import ChatGroq
import os
from models import PaperState

from dotenv import load_dotenv
load_dotenv()
from Helpersfunctions.progress import append_progress


#os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")

def structured_narrative_tool(state: PaperState) -> PaperState:
    """
    Enhance the storytelling version of the research methodology
    into a more cohesive, structured, and engaging narrative.
    Focus on improving flow, transitions, and readability — 
    without adding humor or changing meaning.
    """
    print("🧠 Starting Narrative  tool...")
    feedback = state.last_feedback
    append_progress("😂 Starting structured_narrative_tool with the feedback shared by the reader agent and the feedback is:"+feedback[:100])
    
    chat_groq = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="openai/gpt-oss-safeguard-20b")
    
    story_text = state.report
    print("Getting error after summary_text")
    #feedback = state.last_feedback
    
    if feedback:
        print(f"🔹 Incorporating structured_narrative_tool feedback into Humor creator:\n{feedback}")
        
        # Your humor processing logic here
        humor_result = "Processed humor with feedback..."
    else:
        return state

    # ---- System message defines purpose, tone, and boundaries ----
    system_message = (
    "You are a professional editorial refiner and narrative architect who polishes structured research explanations "
    "into seamless, publication-ready narratives.\n\n"

    "🎯 Objective:\n"
    "- Refine the provided draft into a **clear, coherent, and engaging narrative** suitable for a Medium-style blog.\n"
    "- Keep all technical meaning, sequence, and logic intact — no paraphrasing or invention.\n"
    "- Focus solely on **narrative flow, transitions, rhythm, and readability**.\n"
    "- Smooth abrupt section changes and ensure logical continuity from start to finish.\n"
    "- Make each paragraph revolve around a single main idea, splitting or merging where needed.\n"
    "- When analogies or quotes are present, briefly expand them for context and emotional clarity.\n\n"

    "🪶 Tone and Style:\n"
    "- Balanced, engaging, and professional — like a science communicator writing for an informed audience.\n"
    "- Maintain a natural storytelling flow using transitional phrases (e.g., 'To build on this...', 'Next...', 'As a result...').\n"
    "- Keep paragraphs concise (1–3 sentences) for rhythm and readability.\n"
    "- Avoid redundancy or disjointed jumps between ideas.\n\n"

    "📘 Structure Refinement Goals:\n"
    "1️⃣ Strengthen transitions between motivation, method, and results sections.\n"
    "2️⃣ Ensure one central idea per paragraph — improve pacing and structure.\n"
    "3️⃣ Enhance existing analogies or contextual remarks for clarity and relatability.\n"
    "4️⃣ Preserve a consistent narrative arc: **problem → process → outcome**.\n\n"

    "⚙️ Rules:\n"
    "- Apply reader feedback precisely and only where relevant.\n"
    "- Do NOT change factual or technical content.\n"
    "- Do NOT add new examples, analogies, or ideas.\n"
    "- Keep original meaning and order exactly the same.\n"
    "- Return **only the final refined Markdown article**, ready for publication.\n\n"

    "⚠️ STRICT OUTPUT RULES:\n"
    "- Never include reasoning, thought process, or self-talk.\n"
    "- No '<think>' or 'analysis' text.\n"
    "- Output must look like a polished Medium-style article — not a model reply or explanation."
)


    user_message = (
    f"Here is the current narrative draft that needs refinement:\n\n"
    f"\"\"\"\n{story_text}\n\"\"\"\n\n"
    f"Reader feedback to address (if any):\n\n"
    f"\"\"\"\n{feedback if feedback else 'No feedback provided.'}\n\"\"\"\n\n"
    "Your task:\n"
    "- Improve **only** the areas mentioned in the feedback (if any).\n"
    "- Refine transitions, paragraph flow, and readability while keeping all content accurate.\n"
    "- Ensure smooth logical progression and narrative continuity.\n"
    "- Maintain the Medium-style structure — clean, rhythmic, and engaging.\n\n"
    "Return **only the final, refined Markdown blog post**, without explanations or extra commentary."
)



    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    try:
        response = chat_groq.invoke(messages)
        humorized_story = response.content.strip() if hasattr(response, "content") else str(response).strip()
    except Exception as e:
        humorized_story = f"Error generating humor with ChatGroq: {e}"

    # Store humorized output in both report and humor_text so downstream code can access it
    print("😂 Contextual humor-enhanced storytelling generated successfully with ChatGroq.")
    state.report = humorized_story
    state.humor_text = humorized_story
    append_progress("✅ Narrative tool naration is completed")
    return state
