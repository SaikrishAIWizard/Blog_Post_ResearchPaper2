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
    chat_groq = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.1-8b-instant")
    append_progress("Methodology agent is Working on it to extract the methodology only from the pdf text. It takes some time please wait...")

    text = state.text
    if not text:
        state.methodology_summary = "No paper text available for methodology extraction."
        return state

    # Keep original text intact and process for methodology extraction
    original_text = text

    # Split text into chunks (to avoid token overflow)
    chunk_size = 5000
    chunks = [original_text[i:i + chunk_size] for i in range(0, len(original_text), chunk_size)]

    methodology_parts = []

    # System message defines behavior clearly
    system_message = (
    "You are a precise academic summarizer specializing in reconstructing the *methodology* "
    "sections of research papers from multiple text chunks.\n\n"
    "Your job is to extract, clarify, and organize all **technical and procedural details** "
    "that describe *how the proposed method works*.\n\n"
    "⚙️ Focus on:\n"
    "- Experimental design, architecture, workflow, data handling, algorithms, and training.\n"
    "- Preserving factual accuracy and domain terminology.\n"
    "- Maintaining continuity — assume earlier or later chunks may describe related parts.\n"
    "- Avoid repeating introduction or conclusion if already implied.\n\n"
    "📘 Output Guidelines:\n"
    "- Return a well-organized Markdown structure (headings, subpoints, and lists where helpful).\n"
    "- Keep tone professional and factual — no storytelling or creative phrasing.\n"
    "- Avoid summary words like 'In conclusion' or 'Overall' — this is not the end of the paper.\n"
    "- Focus only on extracting all methodology-related information from this chunk.\n"
    "- If no methodology content is found, return an empty string.\n")

    # Process each chunk (process all chunks by default)
    print(f"🧩 Total chunks to process for methodology extraction: {len(chunks)}")
    append_progress(f"Starting methodology extraction: {len(chunks)} chunks")
    for idx, chunk in enumerate(chunks):
        print(f"🧩 Processing chunk {idx + 1}/{len(chunks)} for Methodology expert structuring...")
        append_progress(f"🧩 Processing chunk {idx + 1}/{len(chunks)} for Methodology expert structuring...")
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": (f"Read the following research paper text chunk carefully and extract ONLY the parts "
    f"that describe the **methodology** — i.e., how the proposed system, model, or experiment works.\n\n"
    f"Paper Chunk {idx+1}:\n{chunk}\n\n"
    f"Return only the extracted methodology text, keeping all technical details intact. "
    f"If none is found, return an empty string.")}
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
