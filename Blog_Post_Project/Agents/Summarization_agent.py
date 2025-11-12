from langchain_groq import ChatGroq
import os
from models import PaperState
import re
from dotenv import load_dotenv
from Helpersfunctions.progress import append_progress
load_dotenv()

#os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")

def summarize_text_node(state: PaperState) -> PaperState:
    """
    Extract only the 'Methodology' section from each chunk of the research paper using ChatGroq.
    Combines all extracted methodology parts into a single unified text.
    """
    #chat_groq = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="openai/gpt-oss-20b")
    chat_groq = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="openai/gpt-oss-20b")

    text = state.text
    if not text:
        state.methodology_summary = "No paper text available for methodology extraction."
        return state

    # Keep original text intact and process for methodology extraction
    original_text = text

    # Split text into chunks (to avoid token overflow)
    chunk_size = 10000
    chunks = [original_text[i:i + chunk_size] for i in range(0, len(original_text), chunk_size)]

    methodology_parts = []

    # System message defines behavior clearly
    system_message = (
        "You are an expert in reading and extracting scientific content.\n"
        "Your task is to extract ONLY the **Methodology** part from the given research paper text.\n"
        "Ignore introduction, abstract, objectives, results, discussion, and conclusion.\n\n"
        "When you find methodology details, include all relevant technical descriptions:\n"
        "- Datasets, architectures, algorithms, models, training processes\n"
        "- Tools, experimental setup, evaluation pipeline, or data flow steps\n\n"
        "If methodology information isn't present, return nothing for that chunk.\n"
        "Return plain text, not Markdown or lists.\n\n"
    )

    # Process each chunk (process all chunks by default)
    print(f"🧩 Total chunks to process for methodology extraction: {len(chunks)}")
    append_progress(f"Starting methodology extraction: {len(chunks)} chunks")
    for idx, chunk in enumerate(chunks):
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Paper Chunk {idx+1}:\n{chunk}"}
        ]

        try:
            response = chat_groq.invoke(messages)
            extracted = response.content.strip() if hasattr(response, "content") else str(response).strip()
        except Exception as e:
            extracted = f"[Error extracting from chunk {idx+1}: {e}]"

        if extracted:
            methodology_parts.append(extracted)

    # Merge all extracted methodology segments
    combined_methodology = "\n\n".join(methodology_parts).strip()

    # Optional: Deduplicate overlapping lines
    combined_methodology = re.sub(r'(\b[\w\s,.-]{10,}\b)(?:\s+\1)+', r'\1', combined_methodology)


    # Assign methodology to its own field and preserve full text
    state.methodology_summary = (
        "## Methodology\n"
        f"{combined_methodology if combined_methodology else 'No methodology content extracted.'}"
    )

    # Keep original extracted text in state.text for downstream processing
    state.text = combined_methodology

    print("🧩 Methodology extraction complete using ChatGroq.")
    print(f"Extracted methodology length: {len(combined_methodology)} chars")
    append_progress(f"Methodology extraction complete: {len(combined_methodology)} chars")
    return state
