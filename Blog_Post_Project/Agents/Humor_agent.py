from langchain_groq import ChatGroq
import os, time, tiktoken, re
from models import PaperState
from dotenv import load_dotenv
from Helpersfunctions.progress import append_progress

load_dotenv()

def structured_narrative_node(state: PaperState) -> PaperState:
    """
    Enhances the storytelling version of the research methodology into a more cohesive,
    structured, and engaging narrative. Focuses on improving readability, transitions,
    and flow — without altering technical meaning or inventing new content.
    """

    # ✅ Use a high-context reasoning model
    chat_groq = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="openai/gpt-oss-safeguard-20b"
    )

    append_progress("🧠 Structured Narrative agent is refining the storytelling text for clarity and smooth flow...")

    story_text = state.text.strip() if state.text else ""
    if not story_text:
        #state.structured_narrative = "⚠️ No storytelling text available for refinement."
        return state

    # --- Tokenizer-based safe chunking ---
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(story_text)
    max_chunk_tokens = 2500  # safe context size for Groq models
    chunks = [enc.decode(tokens[i:i + max_chunk_tokens]) for i in range(0, len(tokens), max_chunk_tokens)]

    print(f"🧩 Split storytelling text into {len(chunks)} manageable chunks for structured refinement.")
    append_progress(f"🧩 Split storytelling text into {len(chunks)} chunks for processing...")

    # --- System message defining tone, goals, and style ---
    system_message = (
        "You are an expert editorial refiner who transforms structured research explanations "
        "into polished, publication-ready narratives. "
        "Your goal is to preserve the original meaning and technical accuracy while enhancing clarity, rhythm, and narrative flow.\n\n"

        "🎯 **Objective:**\n"
        "- Refine the text into a **well-structured, logically coherent story**.\n"
        "- Maintain all technical details and sequence — do not add or remove content.\n"
        "- Focus on **flow, cohesion, and readability** — ensure smooth transitions between sections.\n"
        "- Each paragraph should focus on one central idea.\n"
        "- Where analogies or quotes exist, expand slightly for context and emotional resonance.\n"
        "- Strengthen the connection between introduction, methodology, and conclusion.\n\n"

        "🪶 **Tone & Style:**\n"
        "- Balanced and professional — like a science journalist polishing a research article.\n"
        "- Use smooth connectors (e.g., 'Building on this...', 'This leads to...', 'In essence...').\n"
        "- Maintain short paragraphs and steady pacing.\n"
        "- Avoid redundancy and jargon.\n\n"

        "📘 **Structure Goals:**\n"
        "1️⃣ Strengthen transitions between motivation and methodology.\n"
        "2️⃣ Keep one idea per paragraph — split dense ones if necessary.\n"
        "3️⃣ Refine analogies or examples for clarity.\n"
        "4️⃣ Ensure logical flow from input → process → output.\n\n"

        "⚙️ **Rules:**\n"
        "- Do not add, remove, or alter factual information.\n"
        "- Do not include reasoning, thought processes, or system notes.\n"
        "- Return only the **final refined Markdown text**, ready for publication.\n"
    )

    refined_parts = []

    # --- Retry-safe invoke helper ---
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
        return "⚠️ Error processing this section."

    # --- Process chunks sequentially ---
    for idx, chunk in enumerate(chunks):
        print(f"✍️ Refining narrative chunk {idx + 1}/{len(chunks)}...")
        append_progress(f"✍️ Refining narrative chunk {idx + 1}/{len(chunks)}...")

        user_message = (
            f"Here is section {idx + 1} of the storytelling text:\n\n"
            f"---\n{chunk}\n---\n\n"
            "Refine this section into a smoother, publication-ready version "
            "while keeping all technical details and logical flow intact."
        )

        refined_output = safe_invoke([
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ])

        refined_parts.append(refined_output)

    # --- Merge refined sections ---
    full_refined_text = "\n\n".join(refined_parts).strip()

    # --- Clean duplicate headers or repeated lines ---
    full_refined_text = re.sub(r'(#+.*?)(\n\s*#+.*?)+', r'\1', full_refined_text, flags=re.S)

    # --- Save results ---
    state.text = full_refined_text
    #state.structured_narrative = full_refined_text

    print("✅ Structured narrative successfully refined and polished.")
    append_progress("✅ Structured narrative refinement completed successfully.")

    return state
