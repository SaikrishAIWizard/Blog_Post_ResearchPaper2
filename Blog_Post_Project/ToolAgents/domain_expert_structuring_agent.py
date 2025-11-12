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
    append_progress("🧠 Starting domain expert structuring tool...")
    
    feedback = state.last_feedback

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
    system_message = {
        "role": "system",
        "content": (
            "You are a precise academic summarizer that restructures research methodologies "
            "into technically organized Markdown summaries for better understanding."
            f"Reader feedback (if any) to improve extraction: {feedback}"
        )
    }

    user_message = {
    "role": "user",
    "content": f"""
You are given the final report text of a research paper in **{domain_expert}**:

\"\"\"
{methodology_text}
\"\"\"

Reviewer feedback highlights issues:

\"\"\"
{feedback}
\"\"\"

Your task: **improve only the parts mentioned in the feedback**.  
Do NOT change parts that are fine. Preserve the original wording and flow where no improvements are needed.

Respond **only with the updated methodology text**, no extra explanations or comments.
"""
}

    try:
        response = chat_groq.invoke([system_message, user_message])
        structured_output = (
            response.content.strip()
            if hasattr(response, "content")
            else str(response)
        )

        structured_result = structured_output
        print(f"🧠 Structured methodology created ({domain_expert}).")

    except Exception as e:
        structured_result = f"⚠️ Error during structuring: {e}"
    state.report = structured_result
    state.methodology_summary = structured_result
    # Ensure we return the modified state so the workflow can continue
    append_progress("✅ Domain expert structuring complete")
    return state

