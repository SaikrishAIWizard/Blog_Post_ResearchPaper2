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

    chat_groq = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="openai/gpt-oss-20b")
    # feedback = state.last_feedback
    # append_progress("🎯 Starting storytelling enhancement")
    feedback = state.last_feedback
    append_progress("😂 Starting storytelling enhancement with the feedback shared by the reader agent and the feedback is:"+feedback[:100])
    
    if feedback:
        print(f"🔹 Incorporating reader feedback into storytelling telling creator:\n{feedback}")

    summary_text = state.report
    if not summary_text:
        state.story_text = "No methodology available for storytelling."
        return state

    # ---- System message defines purpose and tone ----
    system_message = (
    "You are a world-class research storytelling editor. "
    "Your job is to refine an existing research blog draft based strictly on reviewer feedback.\n\n"

    "🎯 Objective:\n"
    "- Improve the **storytelling flow, coherence, and readability** of the existing draft.\n"
    "- Focus entirely on implementing the reviewer’s feedback — especially SPECIFIC_ISSUES and ACTION_ITEMS.\n"
    "- Keep the existing meaning, tone, and structure intact.\n"
    "- Your goal is *incremental narrative improvement*, not rewriting from scratch.\n\n"

    "🪶 Tone and Style:\n"
    "- Maintain the author’s original voice and tone.\n"
    "- Strengthen **transitions** and ensure smooth connections between sections.\n"
    "- Simplify dense or overly technical sentences for clarity, but preserve precision.\n"
    "- Use short paragraphs and rhythmic flow for readability.\n"
    "- Avoid excessive humor or analogies unless explicitly suggested by feedback.\n"
    "- Keep the writing natural, conversational, and cohesive — like a well-edited Medium article.\n\n"

    "⚙️ Rules:\n"
    "- Do NOT invent or add new ideas.\n"
    "- Do NOT summarize or explain feedback — just apply it.\n"
    "- Do NOT output reasoning or '<think>' text.\n"
    "- Return ONLY the final, improved Markdown-formatted article — ready for publication.\n"
    "- The article must feel refined and smoother, but still true to the original author’s draft."
)

    user_message = (
    f"Here is the current version of the research storytelling draft:\n\n"
    f"{summary_text}\n\n"
    f"Here is the reviewer feedback you must apply:\n\n"
    f"{feedback}\n\n"
    "Now revise the blog based on this feedback. Focus only on improving the areas mentioned in the feedback, "
    "such as transitions, narrative flow, readability, and engagement. Do not alter structure or meaning — "
    "only refine the storytelling quality."
)


    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    try:
        response = chat_groq.invoke(messages)
        story_output = response.content.strip() if hasattr(response, "content") else str(response).strip()
    except Exception as e:
        #story_output = f"Error generating storytelling output with ChatGroq: {e}"
        append_progress(f"Error generating storytelling output with ChatGroq: {e}")
        story_output = summary_text
    # Store in both the generic report field and the dedicated story field
    state.report = story_output
    #state.story_text = story_output
    print("🎯 Feedbacked Methodology storytelling generated successfully with ChatGroq.")
    append_progress("✅ Storytelling enhancement complete")
    return state
