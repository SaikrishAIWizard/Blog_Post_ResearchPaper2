import os
import re
import tiktoken
from langchain_groq import ChatGroq
from models import PaperState
from dotenv import load_dotenv
from Helpersfunctions.progress import append_progress

load_dotenv()

def summarize_text_node(state: PaperState) -> PaperState:
    """
    Extracts the 'Methodology' section from a research paper using ChatGroq.
    Uses tiktoken for safe chunking and avoids model context overflow.
    """
    chat_groq = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.1-8b-instant")

    append_progress("⚙️ Methodology agent working on extraction... Please wait, this may take a few minutes.")

    text = state.text
    if not text:
        state.methodology_summary = "⚠️ No paper text available for methodology extraction."
        return state

    original_text = text.strip()

    # --- Tokenizer-based safe chunking (tiktoken: no auth, lightweight) ---
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(original_text)
    max_chunk_tokens = 3000  # ~safe context size
    chunks = [enc.decode(tokens[i:i + max_chunk_tokens]) for i in range(0, len(tokens), max_chunk_tokens)]

    methodology_parts = []

    # --- System instruction for LLM ---
    system_message = (
        "You are an expert scientific content extractor specializing in *methodology* reconstruction.\n\n"
        "🎯 Your job:\n"
        "- Identify and extract **only methodology-related content** from the given text.\n"
        "- Include all relevant details about **workflow, algorithms, architectures, datasets, training, evaluation, and implementation steps**.\n"
        "- Maintain **technical precision** and **logical completeness** — assume the methodology may span across chunks.\n"
        "- Skip unrelated content (introduction, abstract, results, discussions, etc.).\n\n"
        "🧩 Output:\n"
        "- Return a clean, structured Markdown-style extract.\n"
        "- Do NOT add conclusions, summaries, or personal comments.\n"
        "- If this chunk contains no methodology, return an empty string."
    )

    print(f"🧩 Total chunks to process: {len(chunks)}")
    append_progress(f"Processing {len(chunks)} methodology chunks...")

    # --- Safe LLM call ---
    def safe_invoke(messages):
        try:
            return chat_groq.invoke(messages)
        except Exception as e:
            if "Request too large" in str(e):
                print("⚠️ Chunk too large — skipping to prevent overload.")
                append_progress("⚠️ Skipped one large chunk due to token overflow.")
                return None
            else:
                print(f"❌ LLM invocation failed: {e}")
                append_progress(f"❌ LLM invocation failed: {e}")
                return None

    # --- Iterate over chunks ---
    for idx, chunk in enumerate(chunks):
        print(f"🧩 Processing chunk {idx + 1}/{len(chunks)}...")
        append_progress(f"🧩 Extracting methodology from chunk {idx + 1}/{len(chunks)}...")

        user_message = (
            f"Read the following research paper text carefully and extract **only methodology-related content** — "
            f"details on how the system, model, or experiment works.\n\n"
            f"---\n{chunk}\n---\n\n"
            f"Return only the methodology details in Markdown form."
        )

        response = safe_invoke([
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ])

        if response and hasattr(response, "content"):
            extracted = response.content.strip()
            if extracted:
                methodology_parts.append(extracted)
        else:
            print(f"⚠️ Skipping chunk {idx + 1} due to empty or failed response.")
            append_progress(f"⚠️ Skipping chunk {idx + 1} due to empty or failed response.")

    # --- Merge all extracted segments ---
    combined_methodology = "\n\n".join(methodology_parts).strip()

    # --- Deduplicate overlapping lines ---
    combined_methodology = re.sub(r'(\b[\w\s,.-]{20,}\b)(?:\s+\1)+', r'\1', combined_methodology)

    # --- Save final methodology ---
    state.methodology_summary = (
        "## Methodology\n\n"
        f"{combined_methodology if combined_methodology else 'No methodology content extracted.'}"
    )

    # Keep extracted text for next pipeline steps
    state.text = combined_methodology

    print(f"✅ Methodology extraction complete. Total length: {len(combined_methodology)} chars")
    append_progress(f"✅ Methodology extraction complete: {len(combined_methodology)} chars")

    return state
