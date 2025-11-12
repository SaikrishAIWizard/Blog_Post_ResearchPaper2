from langchain_groq import ChatGroq
from models import PaperState
from dotenv import load_dotenv
import os
load_dotenv()

# Utility function to split large text into safe chunks (adjust chunk_size for tokens if needed)
def split_text_into_chunks(text, chunk_size=4000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def domain_expert_structuring_node(state: PaperState) -> PaperState:
    """
    Safely infer domain expert and structure methodology text into a precise technical summary using Groq LLM.
    Chunking is used to avoid request size errors.
    """
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
    chunks = split_text_into_chunks(methodology_text, chunk_size=10000)
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
        system_message = {
            "role": "system",
            "content": (
                "You are a precise academic summarizer that restructures research methodologies "
                "into technically organized Markdown summaries for better understanding."
            )
        }
        user_message = {
            "role": "user",
            "content": f"""
You are given the extracted *methodology* section of a research paper in the field of **{domain_expert}**.
Here is a chunk of the methodology text (chunk {idx + 1}/{len(chunks)}):
\"\"\"
{chunk}
\"\"\"

Your task is to extract and organize all **technical, procedural, and logical steps**
that explain *how the proposed method works* — from design to execution.

Focus on *workflow clarity* — the exact process, mechanism, and reasoning behind each stage.
Avoid general summaries, theoretical discussion, or unrelated information.

Your response should be structured in **Markdown** as follows:

### 1. Core Objective
### 2. Working Principle / Underlying Logic
### 3. Step-by-Step Workflow
### 4. System / Model Architecture
### 5. Data Handling and Processing
### 6. Algorithms and Key Operations
### 7. Implementation and Experimental Setup
### 8. Evaluation and Performance Analysis
### 9. Observed Behaviors and Technical Insights
### 10. Summary of the Working Mechanism

If a section is not described in the text, include:
**Not specified in the text.**
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
    return state
