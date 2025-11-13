import os
import re
import time
import tiktoken
from langchain_groq import ChatGroq
from models import PaperState
from dotenv import load_dotenv
from Helpersfunctions.progress import append_progress

load_dotenv()

def domain_expert_structuring_node(state: PaperState) -> PaperState:
    """
    Infers research domain and restructures methodology text into a clean, technically organized
    Markdown summary suitable for storytelling or blog conversion.
    Uses token-safe chunking and retry logic to handle large inputs.
    """
    append_progress("🧠 Domain Expert is analyzing and structuring the methodology... Please wait...")

    # --- Initialize LLM ---
    chat_groq = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="qwen/qwen3-32b"
    )

    methodology_text = state.text.strip() if state.text else ""
    if not methodology_text:
        state.research_paper_domain = "⚠️ No methodology content provided for structuring."
        return state

    print("📏 Methodology text length:", len(methodology_text))

    # --- Tokenizer-based safe chunking (tiktoken → lightweight, no login needed) ---
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(methodology_text)
    max_chunk_tokens = 3000  # safe for qwen-32b on Groq
    chunks = [enc.decode(tokens[i:i + max_chunk_tokens]) for i in range(0, len(tokens), max_chunk_tokens)]

    print(f"🧩 Split methodology text into {len(chunks)} safe chunks for processing.")
    append_progress(f"🧩 Split methodology text into {len(chunks)} chunks...")

    # --- Step 1: Auto-detect research domain using first chunk ---
    try:
        detect_response = chat_groq.invoke([
            {"role": "system", "content": "Identify the research domain based on methodology content."},
            {"role": "user", "content": (
                f"Given this methodology, identify the most likely research domain "
                f"(e.g., AI, Biotech, Robotics, NLP, Cybersecurity):\n\n{chunks[0]}"
            )}
        ])
        domain_expert = detect_response.content.strip()
        state.domain_expert = domain_expert or "General Research Domain"
    except Exception as e:
        domain_expert = "General Research Domain"
        state.domain_expert = domain_expert
        state.research_paper_domain = f"⚠️ Error detecting domain: {e}"
        return state

    # --- System message for all chunks ---
    system_message = {
        "role": "system",
        "content": (
            "You are an expert academic analyst and technical writing specialist.\n\n"
            "🎯 **Objective:**\n"
            "Transform the given research *methodology* into a structured, technically clear, and well-formatted Markdown summary.\n"
            "- Focus on logical clarity: problem → concept → system → workflow → results.\n"
            "- Include as many **technical and procedural details** as possible (datasets, algorithms, architecture, training, evaluation).\n"
            "- Keep the structure consistent across all chunks.\n\n"
            "📘 **Expected Markdown Format:**\n"
            "### 1. Problem & Objective\n"
            "### 2. Conceptual Foundation / Core Idea\n"
            "### 3. System Design / Architecture\n"
            "### 4. Workflow & Process Steps\n"
            "### 5. Data Preparation & Processing\n"
            "### 6. Algorithms & Techniques\n"
            "### 7. Experimental Setup\n"
            "### 8. Evaluation & Validation\n"
            "### 9. Observations & Technical Insights\n"
            "### 10. Summary of Method Operation\n\n"
            "⚙️ **Rules:**\n"
            "- Maintain factual accuracy; do not assume missing details.\n"
            "- Use short paragraphs and bullet points for clarity.\n"
            "- If any section has no info, include: **Not specified in the text.**\n"
            "- Return only the clean Markdown content, no commentary or reasoning."
        )
    }

    chunk_summaries = []

    # --- Retry-safe invoke ---
    def safe_invoke(messages, retries=2):
        for attempt in range(retries):
            try:
                response = chat_groq.invoke(messages)
                if hasattr(response, "content"):
                    return response.content.strip()
                return str(response).strip()
            except Exception as e:
                print(f"⚠️ Attempt {attempt + 1} failed: {e}")
                time.sleep(2)
        return f"⚠️ Error after {retries} retries."

    # --- Step 2: Process chunks sequentially ---
    for idx, chunk in enumerate(chunks):
        print(f"🧩 Processing chunk {idx + 1}/{len(chunks)} for domain expert structuring...")
        append_progress(f"Processing chunk {idx + 1}/{len(chunks)}...")

        user_message = {
            "role": "user",
            "content": (
                f"You are analyzing a portion of the *Methodology* section (chunk {idx + 1}/{len(chunks)}) "
                f"from a research paper in **{domain_expert}**.\n\n"
                f"---\n{chunk}\n---\n\n"
                "Restructure this chunk into the specified Markdown format above, ensuring completeness and logical clarity."
            )
        }

        structured_output = safe_invoke([system_message, user_message])
        chunk_summaries.append(f"## Methodology Chunk {idx + 1}\n\n{structured_output}")

    # --- Step 3: Merge structured outputs ---
    combined_summary = "\n\n".join(chunk_summaries).strip()

    # Deduplicate repeated headers
    combined_summary = re.sub(r'(#+.*?)(\n\s*#+.*?)+', r'\1', combined_summary, flags=re.S)

    # --- Save results ---
    state.text = combined_summary
    state.research_paper_domain = combined_summary

    print(f"✅ Domain Expert Structuring complete for {domain_expert} ({len(chunks)} chunks).")
    append_progress(f"✅ Domain Expert Structuring complete for {domain_expert}.")
    return state
