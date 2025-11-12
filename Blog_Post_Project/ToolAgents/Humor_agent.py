from langchain_groq import ChatGroq
import os
from models import PaperState

from dotenv import load_dotenv
load_dotenv()
from Helpersfunctions.progress import append_progress


#os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")

def humor_tool_node(state: PaperState) -> PaperState:
    """
    Add contextual, intelligent humor to the storytelling explanation while keeping it
    accurate, engaging, and professionally entertaining using ChatGroq.
    """
    print("🧠 Starting humor  tool...")
    append_progress("😂 Starting humor enhancement")
    
    chat_groq = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="openai/gpt-oss-safeguard-20b")
    
    story_text = state.report
    print("Getting error after summary_text")
    feedback = state.last_feedback
    
    if feedback:
        print(f"🔹 Incorporating reader feedback into Humor creator:\n{feedback}")
        
        # Your humor processing logic here
        humor_result = "Processed humor with feedback..."
    else:
        return state

    # ---- System message defines purpose, tone, and boundaries ----
    system_message = (
        "You are a witty yet professional AI science communicator — a blend of Randall Munroe (xkcd), "
        "Bill Nye, and Andrej Karpathy on coffee.\n\n"
        "Your mission: Add light, intelligent humor to a research storytelling explanation "
        "without altering its meaning, flow, or technical correctness.\n\n"
        "🎯 Goals:\n"
        "- Keep the story *accurate and engaging*.\n"
        "- Insert **contextual humor** naturally where it enhances understanding or reader enjoyment.\n"
        "- Make complex technical ideas feel friendly and relatable.\n"
        "- Use emojis and styled text (bold, italics) sparingly for emphasis.\n"
        "- Humor should sound like a **human narrator smiling while explaining**, not a stand-up comedian.\n\n"
        "🧠 Humor Guidelines:\n"
        "- ✅ Use clever analogies, puns, or relatable examples tied to AI, coding, or data.\n"
        "- ✅ Add short humorous asides or one-liners where appropriate.\n"
        "- ✅ Keep humor relevant to the context (e.g., model training, debugging, data cleaning, etc.).\n"
        "- ✅ Maintain a logical, continuous narrative — humor should *fit*, not interrupt.\n"
        "- ❌ Avoid sarcasm, pop culture overload, or jokes unrelated to the topic.\n"
        "- ❌ Never distort or replace any technical detail.\n\n"
        "✨ Example tone snippets:\n"
        "- 'The dataset was cleaned — think of it as a digital detox for messy data.'\n"
        "- 'The model learned faster than an intern realizing there's free pizza in the office.'\n"
        "- 'Backpropagation: where your model regrets its mistakes and tries again — like all of us after a bad tweet.'\n\n"
        "💬 Format & Style:\n"
        "- Use a smooth, story-driven tone — like narrating a fun science documentary.\n"
        "- Use emojis thoughtfully (e.g., 🤖, 🧠, 💡, 🔍, ⚙️, 😂, 🚀).\n"
        "- Style some words or phrases in **bold** or *italics* to highlight humor or key ideas.\n"
        "- The humor should make the text *more readable*, not distracting.\n"
        "Keep paragraphs natural and cohesive — this is still an academic storytelling piece with personality."
        f"Reader feedback (if any) to improve extraction: {feedback}"
    )

    # ---- User message provides the storytelling text ----
    user_message = (
    f"Here is the final report we need to improve:\n\n"
    f"{story_text}\n\n"
    f"Reviewer feedback highlights areas to improve:\n\n"
    f"{feedback}\n\n"
    "Your task: **enhance only the parts mentioned in the feedback** with intelligent, contextual humor "
    "that fits naturally. Keep the original meaning and technical flow intact. "
    "Add emojis and light style (bold, italics) to improve readability and engagement, "
    "but don't overuse them. Return the full humor-enhanced story text only, no extra explanations."
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
    append_progress("✅ Humor enhancement complete")
    return state
