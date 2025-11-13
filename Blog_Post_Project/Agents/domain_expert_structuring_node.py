from langchain_groq import ChatGroq
from models import PaperState
from dotenv import load_dotenv
import os
from Helpersfunctions.progress import append_progress
load_dotenv()

# Utility function to split large text into safe chunks (adjust chunk_size for tokens if needed)
def split_text_into_chunks(text, chunk_size=4000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def domain_expert_structuring_node(state: PaperState) -> PaperState:
    """
    Safely infer domain expert and structure methodology text into a precise technical summary using Groq LLM.
    Chunking is used to avoid request size errors.
    """
    append_progress("Domain expert is Working on to Explain the methodology.It takes some time please wait...")
    chat_groq = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="qwen/qwen3-32b"
    )

    methodology_text = state.text
    print("length of the methodology text is:", len(methodology_text))

    if not methodology_text:
        state.research_paper = "⚠️ No methodology content provided for structuring."
        return state

    # --- Step 1: Auto-detect domain using the first chunk ---
    chunks = split_text_into_chunks(methodology_text, chunk_size=5000)
    print(f"🧩 Split methodology text into {len(chunks)} chunks for processing.")
    first_chunk = chunks[0]

    try:
        detect_response = chat_groq.invoke([
            {"role": "system", "content": "You identify the relevant technical field based on methodology content."},
            {"role": "user", "content": f"Read the following research methodology and respond with the most suitable domain field (e.g., 'AI', 'Mechanical', 'Biotech', 'Cybersecurity', etc.):\n\n{first_chunk}"}
        ])
        domain_expert = detect_response.content.strip()
        state.domain_expert = domain_expert or "General Research Domain"
    except Exception as e:
        domain_expert = "General Research Domain"
        state.domain_expert = domain_expert
        state.research_paper_domain = f"⚠️ Error during domain detection: {e}"
        return state

    # --- Step 2: Chunked technical extraction ---
    chunk_summaries = []
    for idx, chunk in enumerate(chunks):
        print(f"🧩 Processing chunk {idx + 1}/{len(chunks)} for domain expert structuring...")
        append_progress(f"🧩 Processing chunk {idx + 1}/{len(chunks)} for domain expert structuring...")
        system_message = {
            "role": "system",
            "content": (
    "You are an expert academic analyst and technical writing specialist.\n\n"
    "🎯 **Primary Objective:**\n"
    "Restructure the provided research *methodology* text into a well-organized, "
    "logically connected, and technically complete Markdown summary that clearly explains "
    "how the proposed method works — step by step.\n\n"

    "🧩 **Your Focus:**\n"
    "- Extract and organize **all technical details** into clear, distinct sections.\n"
    "- Present a **logical flow** of ideas — from the problem to the system design, process, and evaluation.\n"
    "- Use precise, academic language but keep it readable for researchers and engineers.\n"
    "- Maintain consistent formatting so that a storytelling agent can easily convert this into a narrative.\n\n"

    "📘 **Expected Output Format (Markdown):**\n"
    "### 1. Problem & Objective\n"
    "Briefly describe what problem the methodology aims to solve and why it matters.\n\n"
    "### 2. Conceptual Foundation / Core Idea\n"
    "Summarize the underlying principle or motivation behind the approach.\n\n"
    "### 3. System Design / Architecture\n"
    "Detail the system’s components, data flow, architecture diagram explanation, or framework design.\n\n"
    "### 4. Workflow & Process Steps\n"
    "List and explain each key stage of the methodology — from input to output.\n\n"
    "### 5. Data Preparation & Processing\n"
    "Describe dataset details, preprocessing steps, transformations, and feature engineering.\n\n"
    "### 6. Algorithms & Techniques\n"
    "Explain the algorithms, models, optimization strategies, or mathematical formulations used.\n\n"
    "### 7. Experimental Setup\n"
    "Include details about training configurations, hardware/software used, hyperparameters, etc.\n\n"
    "### 8. Evaluation & Validation\n"
    "Describe how the methodology’s performance was measured, compared, or validated.\n\n"
    "### 9. Observations & Technical Insights\n"
    "Summarize key findings, technical observations, or limitations noted during implementation.\n\n"
    "### 10. Summary of Method Operation\n"
    "Conclude with a concise explanation of how the entire system works end-to-end.\n\n"

    "🧠 **Stylistic Rules:**\n"
    "- Be **structured, clear, and detailed** — the output should look like a technical report section.\n"
    "- Maintain accuracy — **do not invent or assume** missing data.\n"
    "- Use Markdown headers, lists, and bold text where necessary for clarity.\n"
    "- Preserve technical terminology but avoid redundancy.\n"
    "- Each section should flow naturally into the next — this logical flow will directly support the storytelling agent.\n\n"

    "⚙️ **Output Policy:**\n"
    "- Return only the final, polished Markdown summary.\n"
    "- No reasoning, commentary, or instructions.\n"
    "- Your response should look like a clean academic methodology document, "
    "ready for use in a blog or storytelling phase."
)

        }
        user_message = {
    "role": "user",
    "content": f"""
You are provided with a portion of the *Methodology* section (chunk {idx + 1}/{len(chunks)}) 
from a research paper in the field of **{domain_expert}**.

\"\"\" 
{chunk}
\"\"\"

Your task:
- Carefully read this text and extract **all technical and procedural details** relevant to the methodology.
- Reorganize the extracted information into a clear, structured Markdown format following the format and tone described in the system message.
- Preserve all factual content and sequence — do **not** summarize or shorten.
- Avoid repetition or filler text, but ensure the logical flow between ideas is smooth.
- Include as much **technical specificity** as the text provides (datasets, algorithms, architectures, workflows, evaluation, etc.).

If any section from the expected format (e.g., Workflow, Architecture, Algorithms, etc.) is missing or unclear in this chunk, include the note:
**Not specified in the text.**

Return only the organized Markdown content — no explanations or commentary.
"""
}
        try:
            response = chat_groq.invoke([system_message, user_message])
            structured_output = (
                response.content.strip()
                if hasattr(response, "content")
                else str(response)
            )
            chunk_summaries.append(f"## Methodology Chunk {idx + 1}\n\n{structured_output}")
        except Exception as e:
            chunk_summaries.append(f"## Methodology Chunk {idx + 1}\n\n⚠️ Error processing chunk: {e}")

    # --- Step 3: Aggregate chunked summaries ---
    state.text = "\n\n".join(chunk_summaries)
    state.domain_expert = domain_expert

    print(f"🧠 Structured methodology created for {domain_expert} using {len(chunks)} chunks.")
    
    append_progress(f"🧠 Structured methodology created for {domain_expert} using {len(chunks)} chunks.")
    
    return state
