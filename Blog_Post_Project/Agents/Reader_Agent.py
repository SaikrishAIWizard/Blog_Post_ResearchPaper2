import os
from langchain_groq import ChatGroq
from models import PaperState
from dotenv import load_dotenv

load_dotenv()
#os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


def reader_agent_node(state: PaperState) -> PaperState:
    """
    Evaluates the current blog draft and dynamically decides which node to revisit.
    Loops back based on feedback, stops after 2 iterations.
    """
    report_text = state.get("text", "")
    loop_count = state.get("loop_count", 0)
    last_feedback = state.get("last_feedback", "")
    print(f"🔹 Reader Agent evaluating blog draft (loop count: {loop_count})... previous feedback: {last_feedback}")

    system_message = {
        "role": "system",
        "content": (
            "You are a blog evaluator. "
            "Provide ONLY a numeric rating (1-10) and a single-sentence actionable feedback. "
            "Do NOT add extra explanations, lists, or markdown."
        )
    }

    user_message = {
        "role": "user",
        "content": (
            f"Here is the current blog draft:\n\n{report_text}\n\n"
            f"Loop count so far: {loop_count}\n"
            f"Previous feedback: {last_feedback}\n\n"
            "Instructions:\n"
            "1. Provide ONLY a numeric rating from 1 to 10.\n"
            "2. Provide ONLY a single-sentence actionable feedback.\n"
            "3. If the rating is 8 or higher, indicate the draft is complete and the workflow should END.\n"
            "4. If the rating is less than 8, suggest which node to revisit: "
            "'summarize_text', 'domain_expert', 'storytelling', 'humor', 'visual_illustration_inline'.\n"
            "5. Do NOT exceed a maximum of 5 loops; if loop_count >= 5, workflow should END."
        )
    }

    chat_groq = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="meta-llama/llama-4-maverick-17b-128e-instruct")

    # Pass only strings for content
    messages = [
        {"role": "system", "content": system_message["content"]},
        {"role": "user", "content": user_message["content"]}
    ]

    # Call LLM safely
    try:
        response = chat_groq.invoke(messages)
        feedback_text = response.content.strip() if hasattr(response, "content") else str(response).strip()
    except Exception as e:
        feedback_text = f"LLM error: {e}"

    # Set safe defaults and loop limit
    # if loop_count >= 2 or "generate_report" in feedback_text.lower():
    #     next_node = "generate_report"
    # else:
    #     next_node = ""

    # Update state
    state["loop_count"] = loop_count + 1
    state["last_feedback"] = feedback_text
    # state["next_node"] = next_node
    report_name = state.get("report_file", "ai_paper_report.md")
    with open(report_name, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(f"🔹 Reader agent feedback: {feedback_text[:100]}...")
    state["report"] = report_text
    # print(f"🔹 Next node selected: {next_node}")

    return state
