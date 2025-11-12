import os
from typing import TypedDict, List, Optional

from langchain_core.messages.utils import trim_messages
from langgraph.graph import StateGraph, END
from IPython.display import Image, display
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition

from Agents.Summarization_agent import summarize_text_node
from Agents.Storytelling_agent import storytelling_node
from Agents.Humor_agent import humor_node
from Agents.Visual_Illustration_agent import visual_illustration_inline_node
from Agents.domain_expert_structuring_node import domain_expert_structuring_node
from Agents.Reader_Agent import reader_agent_node

from ToolAgents.domain_expert_structuring_agent import domain_expert_structuring_tool_node
from ToolAgents.Storytelling_agent import storytelling_tool_node
from ToolAgents.Humor_agent import humor_tool_node

from Helpersfunctions.Extract_pdf import extract_pdf_node
from Helpersfunctions.Generate_report import generate_report_node
from Helpersfunctions.Download_ResearchPaper import download_research_paper_node
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, ToolMessage, AIMessage
from langgraph.prebuilt import ToolNode

from models import PaperState
from ToolAgents.select_node_tool import select_node

from dotenv import load_dotenv
load_dotenv()

import time
from Helpersfunctions.progress import append_progress

#os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
#os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
os.environ["HF_TOKEN"]=os.getenv("HF_TOKEN")


#from langchain_core.utils import get_tokenizer
from langchain_core.language_models.base import get_tokenizer


def truncate_by_tokens(text, max_tokens=7000):
    tokenizer = get_tokenizer()  # Use a tokenizer compatible with Groq
    tokens = tokenizer.encode(text)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
        return tokenizer.decode(tokens)
    return text

# Before saving the state, convert messages to a serializable format
def save_state(state):
    # Convert messages to a list of dicts
    serializable_messages = []
    for msg in state.messages:
        if hasattr(msg, "tool_calls"):
            serializable_messages.append({
                "content": msg.content,
                "tool_calls": msg.tool_calls,
                "additional_kwargs": msg.additional_kwargs,
                "response_metadata": msg.response_metadata,
                "id": msg.id,
                "usage_metadata": msg.usage_metadata
            })
        else:
            serializable_messages.append(msg.model_dump())
    state.messages = serializable_messages
    # Save the state as JSON
    with open("state.json", "w") as f:
        f.write(state.model_dump_json())

# ---------- Define State Schema ----------
# class PaperState(TypedDict):
#     pdf_path: str
#     text: Optional[str]
#     images: Optional[List[str]]
#     summary_text: Optional[str]
#     image_summary: Optional[str]
#     report_file: Optional[str]
#     story_text: Optional[str]
#     humor_text: Optional[str]
#     enhanced_text: Optional[str]


def extract_numeric_rating(text: Optional[str]) -> float:
    """Extract a numeric rating (1-10) from an LLM feedback string.

    Returns 0.0 if no numeric rating is found.
    """
    import re
    if not text:
        return 0.0
    # Look for 10 or single digit 1-9, optionally followed by /10
    m = re.search(r"\b(10|[1-9])(?:\s*/\s*10)?\b", str(text))
    if m:
        try:
            return float(m.group(1))
        except Exception:
            return 0.0
    return 0.0


def tool_calling_llm(state: PaperState) -> PaperState:
    """Call the LLM with tools to evaluate the draft and choose the next node.

    Populates `last_feedback`, `reader_rating`, `last_tool_feedback`, `next_node`, and increments `loop_count`.
    """
    report_text = getattr(state, 'report', '')
    loop_count = getattr(state, 'loop_count', 0) or 0
    last_feedback = getattr(state, 'last_feedback', '')
    print("🔹 Tool calling LLM with last feedback...")
    append_progress("Evaluating draft with LLM rating and node selection")

    system_message = (
        "You are a professional blog evaluator with expertise in academic content, storytelling, and humor. "
        "Your task is to:\n"
        "1. Rate the current blog draft (1-10)\n"
        "2. Provide SPECIFIC, ACTIONABLE feedback\n"
        "3. Identify which component needs improvement\n"
        "4. Use the select_node tool to route to the right improvement agent\n\n"
        "Be critical but constructive. If rating >= 9, the draft is complete (END). "
        "Otherwise, guide the agent on EXACTLY what needs to improve and HOW to improve it."
    )

    user_message = (
        f"CURRENT BLOG DRAFT:\n{report_text}\n\n"
        f"CONTEXT:\n"
        f"- Loop count: {loop_count}\n"
        f"- Previous feedback: {last_feedback}\n\n"
        "EVALUATION INSTRUCTIONS:\n"
        "1. Rate the draft on a scale of 1-10 considering:\n"
        "   - Domain accuracy and technical correctness\n"
        "   - Story coherence and narrative flow\n"
        "   - Humor quality, appropriateness, and engagement\n"
        "   - Overall readability and accessibility\n\n"
        "2. Provide feedback in this EXACT format:\n"
        "   RATING: [number]\n"
        "   FEEDBACK: [Detailed critique of the draft]\n"
        "   IMPROVEMENT_TARGET: [domain_expert | storytelling | humor]\n"
        "   SPECIFIC_ISSUES: [List 2-3 specific problems that the selected node should fix]\n"
        "   ACTION_ITEMS: [Concrete suggestions for improvement]\n\n"
        "3. Use the select_node tool to specify which component needs revision:\n"
        "   - If rating >= 9 or loop >= 3: select 'END' (draft is complete)\n"
        "   - If domain accuracy is weak: select 'domain_expert'\n"
        "   - If story flow/coherence is weak: select 'storytelling'\n"
        "   - If humor is missing/inappropriate: select 'humor'\n\n"
        "Be specific about WHAT needs to improve and WHY."
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]

    chat_groq = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="meta-llama/llama-4-maverick-17b-128e-instruct")
    llm_with_tools = chat_groq.bind_tools([select_node])

    try:
        response = llm_with_tools.invoke(messages)
        print(f"🔹 LLM response: {response}")

        # Default
        next_node = "generate_report"

        # Extract structured feedback from response content
        feedback_text = response.content.strip() if hasattr(response, "content") else str(response).strip()
        
        # Parse structured feedback
        specific_issues = "No specific issues identified."
        action_items = "Continue with next improvement phase."
        
        if "SPECIFIC_ISSUES:" in feedback_text:
            try:
                issues_start = feedback_text.index("SPECIFIC_ISSUES:") + len("SPECIFIC_ISSUES:")
                issues_end = feedback_text.index("ACTION_ITEMS:") if "ACTION_ITEMS:" in feedback_text else len(feedback_text)
                specific_issues = feedback_text[issues_start:issues_end].strip()
            except Exception:
                pass
        
        if "ACTION_ITEMS:" in feedback_text:
            try:
                actions_start = feedback_text.index("ACTION_ITEMS:") + len("ACTION_ITEMS:")
                action_items = feedback_text[actions_start:].strip()
            except Exception:
                pass

        # Extract tool call for next node
        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_call = response.tool_calls[0]
            try:
                next_node = tool_call.get("args", {}).get("node_choice", next_node)
            except Exception:
                next_node = getattr(tool_call, 'args', {}).get('node_choice', next_node) if hasattr(tool_call, 'args') else next_node
            print(f"🔹 Tool call detected - selected node: {next_node}")

        rating = extract_numeric_rating(feedback_text)
        print("LLM tool agent response:", response)

    except Exception as e:
        print(f"❌ LLM error: {e}")
        feedback_text = f"LLM error: {e}"
        specific_issues = str(e)
        action_items = "Manual review required"
        rating = 0.0
        next_node = "END"

    # Update state
    state.loop_count = int(loop_count) + 1
    state.last_feedback = feedback_text
    state.reader_rating = float(rating)
    
    # Build comprehensive tool feedback with specific issues and action items
    state.last_tool_feedback = (
        f"📊 Rating: {rating}/10 | 🎯 Next: {next_node}\n"
        f"🔍 Specific Issues:\n{specific_issues}\n"
        f"✅ Action Items:\n{action_items}"
    )
    
    state.next_node = "END" if state.loop_count >= 3 else next_node

    # Save report (ensure report_file exists)
    report_name = getattr(state, 'report_file', None)
    if report_name:
        try:
            os.makedirs(os.path.dirname(report_name) or '.', exist_ok=True)
            with open(report_name, "w", encoding="utf-8") as f:
                f.write(report_text or "")
        except Exception as e:
            print(f"❌ Could not save report file {report_name}: {e}")

    state.report = report_text

    print(f"🔹 Feedback: {feedback_text[:100]}...")
    print(f"🔹 Rating: {rating}/10")
    print(f"🔹 Specific Issues:\n{specific_issues}")
    print(f"🔹 Action Items:\n{action_items}")
    print(f"🔹 Next node selected: {state.next_node}")
    append_progress(f"✅ Rating: {rating}/10 → {state.next_node} | Issues: {specific_issues[:80]}")

    return state


workflow = StateGraph(PaperState)

# Add nodes
workflow.add_node("download_research_paper", download_research_paper_node)
workflow.add_node("extract_pdf", extract_pdf_node)
workflow.add_node("summarize_text", summarize_text_node)
workflow.add_node("domain_expert", domain_expert_structuring_node)
workflow.add_node("storytelling", storytelling_node)
workflow.add_node("humor", humor_node)
#workflow.add_node("visual_illustration_inline", visual_illustration_inline_node)
workflow.add_node("generate_report", generate_report_node)
#workflow.add_node("reader_agent", reader_agent_node)
workflow.add_node("tool_calling_llm", tool_calling_llm)
workflow.add_node("domain_expert_structuring_tool_node",domain_expert_structuring_tool_node)
workflow.add_node("storytelling_tool_node",storytelling_tool_node)
workflow.add_node("humor_tool_node",humor_tool_node)


# Connect main flow
workflow.add_edge("download_research_paper", "extract_pdf")
workflow.add_edge("extract_pdf", "summarize_text")
workflow.add_edge("summarize_text", "domain_expert")
workflow.add_edge("domain_expert", "storytelling")
workflow.add_edge("storytelling", "humor")
#workflow.add_edge("humor", "visual_illustration_inline")


# Main flow into reader_agent
workflow.add_edge("humor", "generate_report")
workflow.add_edge("generate_report", "tool_calling_llm")

# Conditional routing based on tool selection
def route_after_evaluation(state: PaperState):
    """Route to the selected node or END based on tool_calling_llm decision."""
    next_node = state.next_node if state.next_node else "END"
    print(f"🔀 Routing to: {next_node}")
    return next_node

workflow.add_conditional_edges(
    "tool_calling_llm",
    route_after_evaluation,
    {
        "domain_expert": "domain_expert_structuring_tool_node",
        "storytelling": "storytelling_tool_node",
        "humor": "humor_tool_node",
        "END": END
    }
)

workflow.add_edge("domain_expert_structuring_tool_node","tool_calling_llm")
workflow.add_edge("storytelling_tool_node","tool_calling_llm")
workflow.add_edge("humor_tool_node","tool_calling_llm")


# Set entry point
workflow.set_entry_point("download_research_paper")

# Compile graph
graph = workflow.compile()

# Get PNG bytes
png_bytes = graph.get_graph().draw_mermaid_png()

# Save to file
with open("workflow_graph.png", "wb") as f:
    f.write(png_bytes)

print("✅ Workflow saved as workflow_graph.png")
# Display workflow
#display(Image(graph.get_graph().draw_mermaid_png()))
