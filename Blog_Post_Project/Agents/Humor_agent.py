from langchain_groq import ChatGroq
import os
from models import PaperState

from dotenv import load_dotenv
load_dotenv()
from Helpersfunctions.progress import append_progress

#os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")


def structured_narrative_node(state: PaperState) -> PaperState:
    """
    Enhance the storytelling version of the research methodology
    into a more cohesive, structured, and engaging narrative.
    Focus on improving flow, transitions, and readability — 
    without adding humor or changing meaning.
    """

    chat_groq = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.3-70b-versatile")
    append_progress("Structured Narrative agent is Working on it to make the explanation smoother")


    story_text = state.text
    
    if not story_text:
        state.humor_text = "No storytelling text available to add humor."
        return state

    # ---- System message defines purpose, tone, and boundaries ----
    system_message = (
    "You are an expert editorial refiner who specializes in transforming structured research explanations "
    "into polished, publication-ready narratives. "
    "Your goal is to preserve the original meaning and technical accuracy while enhancing clarity, rhythm, and narrative flow.\n\n"

    "🎯 Objective:\n"
    "- Refine the existing narrative into a **well-structured, logically coherent story**.\n"
    "- Maintain all technical details and sequence exactly as they are — do not add or remove content.\n"
    "- Focus on **flow, cohesion, and readability** — ensuring smooth transitions between sections.\n"
    "- Make each paragraph revolve around one central idea for clarity.\n"
    "- Where analogies or quotes exist, expand slightly to give them context or emotional resonance.\n"
    "- Strengthen links between the introduction and methodology explanation to ensure a seamless story arc.\n\n"

    "🪶 Tone and Style:\n"
    "- Balanced and professional — like a science writer polishing a feature article.\n"
    "- Keep the tone engaging yet precise, avoiding jargon when possible.\n"
    "- Use smooth connectors (e.g., 'Building on this...', 'This leads to...', 'In essence...') for flow.\n"
    "- Maintain short paragraphs and consistent pacing.\n"
    "- Avoid redundancy and ensure ideas progress naturally.\n\n"

    "📘 Structure Refinement Goals:\n"
    "1️⃣ Strengthen transitions between introductory motivation and technical explanation.\n"
    "2️⃣ Keep one clear idea per paragraph — split dense sections if necessary.\n"
    "3️⃣ Expand analogies or contextual remarks to make them intuitive and insightful.\n"
    "4️⃣ Preserve logical flow from input → process → output.\n\n"

    "⚙️ Rules:\n"
    "- Do not remove or rephrase factual details.\n"
    "- Do not add new analogies, only elaborate existing ones if needed.\n"
    "- Maintain the original meaning, order, and technical content.\n"
    "- Return **only the final refined Markdown narrative** — no notes or metadata."

    "⚠️ STRICT OUTPUT RULES:\n"
"- Never include reasoning, analysis, or thought process.\n"
"- No '<think>' or 'analysis' text.\n"
"- Return only the final, polished Markdown blog post — ready for publication.\n"
"- The output must look like a cohesive Medium-style article, not a model response."
)

    user_message = (f"""
Here is the draft narrative to refine and structure:

{story_text}

Please improve it into a smoother, publication-ready version:
- Keep the same content and logic.
- Focus on paragraph coherence, transitions, and flow.
- Ensure one key idea per paragraph.
- If analogies or quotes exist, add context or explanation to make them more meaningful.
- Strengthen the link between the introduction and the main methodology explanation.
"""
    )


    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    try:
        response = chat_groq.invoke(messages)
        humorized_story = response.content.strip() if hasattr(response, "content") else str(response).strip()
    except Exception as e:
        humorized_story = f"Error generating Structured narrative with ChatGroq: {e}"
        print(f"Error generating Structured narrative report with ChatGroq: {e}")
        append_progress(f"Error generating Structured narrative with ChatGroq: {e}")

    state.text = humorized_story
    print("😂 Contextual storytelling generated successfully with ChatGroq.")
    return state
