from langchain_groq import ChatGroq
import os
from models import PaperState

from dotenv import load_dotenv
load_dotenv()
from Helpersfunctions.progress import append_progress

#os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")

def storytelling_tool_node(state: PaperState) -> PaperState:
    """
    Explain the extracted methodology as an engaging, structured, and accurate story
    using ChatGroq with clear system+user messages.
    """

    chat_groq = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.1-8b-instant")
    feedback = state.last_feedback
    append_progress("🎯 Starting storytelling enhancement")
    if feedback:
        print(f"🔹 Incorporating reader feedback into Humor creator:\n{feedback}")

    summary_text = state.report
    if not summary_text:
        state.story_text = "No methodology available for storytelling."
        return state

    # ---- System message defines purpose and tone ----
    system_message = (
        "You are a world-class science communicator who specializes in explaining "
        "complex research methods in a structured, story-like way that anyone can understand.\n\n"
        "Your job is to transform the methodology of a research paper into a continuous, "
        "engaging, and logically flowing story — like a guided tour of how the system works.\n\n"
        "🎯 Goals:\n"
        "- Maintain 100% factual accuracy with the original methodology.\n"
        "- Explain **inputs, processes, and outputs** step by step.\n"
        "- Use clean, realistic **real-world analogies** that clarify each step.\n"
        "- Preserve all technical details — models, datasets, architectures, algorithms, etc.\n"
        "- Keep the tone engaging, educational, and visually descriptive.\n\n"
        "🧩 Structure Guidelines:\n"
        "1. **Start** by introducing what problem the method is trying to solve and what goes into it (inputs).\n"
        "2. **Walk through** each stage of the process logically, explaining what happens and why.\n"
        "3. **Illustrate** key technical steps using short, clear analogies or scenarios that help readers visualize the system.\n"
        "4. **End** by summarizing how the process produces meaningful outcomes.\n\n"
        "🖋️ Style:\n"
        "- Write like a teacher explaining a fascinating system.\n"
        "- Keep paragraphs short and naturally connected.\n"
        "- Avoid buzzwords and heavy jargon — simplify without losing accuracy.\n"
        "- Use subtle storytelling tone — not overly dramatic, not overly formal.\n"
        "- Include emojis sparingly for readability and engagement (💡🔍⚙️🚀🧠✨ are good choices).\n\n"
        "🚫 Do NOT add results, conclusions, or future work — focus ONLY on explaining how the methodology works."
        f"Reader feedback (if any) to improve extraction: {feedback}"
    )

    # ---- User message provides methodology text ----
    user_message = (
        f"Here is the final report we need to improve:\n\n"
        f"{summary_text}\n\n"
        f"Reviewer feedback highlights areas to improve:\n\n"
        f"{feedback}\n\n"
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    try:
        response = chat_groq.invoke(messages)
        story_output = response.content.strip() if hasattr(response, "content") else str(response).strip()
    except Exception as e:
        story_output = f"Error generating storytelling output with ChatGroq: {e}"
    # Store in both the generic report field and the dedicated story field
    state.report = story_output
    state.story_text = story_output
    print("🎯 Feedbacked Methodology storytelling generated successfully with ChatGroq.")
    append_progress("✅ Storytelling enhancement complete")
    return state
