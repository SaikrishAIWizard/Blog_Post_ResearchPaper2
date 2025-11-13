from langchain_groq import ChatGroq
from models import PaperState

from dotenv import load_dotenv
load_dotenv()
import os
from Helpersfunctions.progress import append_progress

def domain_expert_structuring_tool_node(state: PaperState) -> PaperState:
    """
    Automatically infer domain expert and structure methodology text 
    into a precise technical summary using Groq LLM.
    """ 
    import os
    chat_groq = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="qwen/qwen3-32b"
    )
    print("🧠 Starting domain expert structuring tool...")
    
    # append_progress("🧠 Starting domain expert structuring tool...")
    
    feedback = state.last_feedback
    append_progress("😂 Starting domain expert enhancement with the feedback shared by the reader agent and the feedback is:"+feedback[:100])
    

    print(f"🔹 Received feedback for structuring:\n{feedback}")
    methodology_text = state.report
    print("Getting error after summary_text")
    
    if feedback:
        print(f"🔹 Incorporating reader feedback into domain expert structuring:\n{feedback}")
        
        # Your domain expert processing logic here
        structured_result = "Processed domain expert structuring with feedback..."
    else:
        return state

    # --- Step 1: Auto-detect domain if not provided ---
    domain_expert = state.domain_expert

    # --- Step 2: Structured technical extraction ---
    system_message = (
    "You are an expert academic editor and technical summarizer who refines research methodology sections "
    "based strictly on reviewer feedback.\n\n"
    "🎯 Objective:\n"
    "- Preserve all original technical content, logic, and formatting.\n"
    "- Apply only the improvements suggested in the reviewer feedback.\n"
    "- Focus on structure, clarity, and flow — do not alter meaning or add new content.\n"
    "- Improve transitions, paragraph organization, and readability where feedback indicates issues.\n\n"
    "🧠 Editing Style:\n"
    "- Keep the tone precise, academic, and coherent.\n"
    "- Strengthen logical transitions and smooth out abrupt sections.\n"
    "- Use concise and clear phrasing without losing technical depth.\n"
    "- Maintain Markdown structure and all factual details.\n\n"
    "⚙️ Rules:\n"
    "- Do NOT add new information or interpretations.\n"
    "- Do NOT explain your edits or output reasoning text.\n"
    "- Return only the final, polished Markdown methodology text — ready for inclusion in the research blog.\n"
    "- Apply feedback improvements accurately and minimally — edit only where required."
)

    user_message = (
    f"You are given the methodology section of a research paper in **{domain_expert}**:\n\n"
    f"\"\"\"\n{methodology_text}\n\"\"\"\n\n"
    f"Here is the reviewer feedback to apply:\n\n"
    f"\"\"\"\n{feedback}\n\"\"\"\n\n"
    "Your task:\n"
    "- Improve only the parts mentioned in the feedback (e.g., flow, transitions, clarity, readability).\n"
    "- Keep all other sections untouched.\n"
    "- Do not add, remove, or reinterpret technical content.\n\n"
    "Respond **only with the updated Markdown methodology text**, no explanations or comments."
)

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    try:
        response = chat_groq.invoke(messages)
        structured_output = (
            response.content.strip()
            if hasattr(response, "content")
            else str(response)
        )

        structured_result = structured_output
        print(f"🧠 Structured methodology created ({domain_expert}).")
        append_progress(f"🧠 Structured methodology created ({domain_expert}).")

    except Exception as e:
        #structured_result = f"⚠️ Error during structuring: {e}"
        append_progress(f"⚠️ Error during structuring: {e}")
        structured_result = methodology_text
    state.report = structured_result
    #state.methodology_summary = structured_result
    # Ensure we return the modified state so the workflow can continue
    append_progress("✅ Domain expert structuring complete")
    return state

