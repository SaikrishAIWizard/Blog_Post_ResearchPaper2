import os, re, requests
from langchain_groq import ChatGroq
from models import PaperState
from dotenv import load_dotenv

load_dotenv()

def visual_illustration_inline_node(state: PaperState) -> PaperState:
    """
    Generate and embed <5 most relevant conceptual cartoon-style image URLs
    directly in Markdown (no local saving).
    """

    # --- Setup ---
    chat_groq = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="openai/gpt-oss-120b")
    content = state.get("humor_text")# or state.get("story_text")
    research_paper = state.get("research_paper", "default_paper").replace(" ", "_")
    feedback = getattr(state, "last_feedback", "")
    if feedback:
        print(f"🔹 Incorporating reader feedback into visual Illustration :\n{feedback}")
        content = state.get("report_text", "").strip()

    if not content:
        state["enhanced_text"] = "No story content available for visual enhancement."
        return state

    # --- Split content into paragraphs ---
    paragraphs = re.split(r"\n\s*\n", content.strip())
    concept_paragraphs = []

    # Identify conceptual / vivid paragraphs
    for idx, para in enumerate(paragraphs):
        if any(keyword in para.lower() for keyword in [
            "data", "model", "training", "evaluation", "system", "architecture",
            "learning", "ai", "robot", "algorithm", "experiment"
        ]):
            concept_paragraphs.append((idx, para))

    # Limit to <5 concepts
    concept_paragraphs = concept_paragraphs[:5] if len(concept_paragraphs) >= 5 else concept_paragraphs

    # --- Google Image Search Helper ---
    def google_image_search(query):
        """Search Google Images via Custom Search API."""
        api_key = os.getenv("GOOGLE_API_KEY")
        cx = os.getenv("GOOGLE_CX")
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "cx": cx,
            "key": api_key,
            "searchType": "image",
            "num": 1,  # fetch top 1 per concept
            "safe": "active"
        }
        try:
            resp = requests.get(url, params=params)
            data = resp.json()
            if "items" in data:
                return data["items"][0]["link"]
            else:
                print(f"❌ No results found. Response: {data}")
                return None
        except Exception as e:
            print(f"⚠️ Google search failed: {e}")
            return None

    enhanced_parts = paragraphs.copy()

    # --- Generate Groq queries & attach image URLs ---
    for idx, para in concept_paragraphs:
        try:
            prompt = (
                f"Generate a short, vivid, cartoon-style Google image search query for this concept:\n\n"
                f"{para}\n\n"
                "Focus on showing how it works. Keep it under 10 words."
                f"Reader feedback (if any) to improve extraction: {feedback}"
            )

            llm_response = chat_groq.invoke(prompt)
            search_query = getattr(llm_response, "content", str(llm_response))
            print(f"🔍 Search Query (Groq): {search_query}")

            image_url = google_image_search(search_query)
            if image_url:
                print(f"🖼️ Found Image URL: {image_url}")
                markdown_img = (
                         f'<p align="center">'
                        f'<img src="{image_url}" alt="Illustration for concept" '
                        f'width="600px" style="border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.2);"/>'
                        f'</p>'
                            )

                #markdown_img = f"![Illustration for concept]({image_url})"
                enhanced_parts.insert(idx * 2 + 1, markdown_img)
            else:
                enhanced_parts.insert(idx * 2 + 1, "<!-- No relevant image found -->")

        except Exception as e:
            enhanced_parts.insert(idx * 2 + 1, f"<!-- Error generating illustration: {e} -->")

    # --- Final Output ---
    state["enhanced_text"] = "\n\n".join(enhanced_parts)
    if feedback:
        state["report"] = "\n\n".join(enhanced_parts)
    print(f"🎨 Added up to {len(concept_paragraphs)} image URLs inline (Markdown-compatible) for {research_paper}.")
    return state








# def visual_illustration_inline_node(state: PaperState) -> PaperState:
#     """Generate and embed 3 relevant conceptual cartoon-style images inline for Markdown output."""

#     # Setup Hugging Face Nebius InferenceClient
#     client = InferenceClient(
#         provider="nebius",
#         api_key=os.environ.get("HF_TOKEN")
#     )

#     content = state.get("humor_text") or state.get("story_text")
#     if not content:
#         state["enhanced_text"] = "No story content available for visual enhancement."
#         return state

#     # Split content into paragraphs
#     paragraphs = re.split(r"\n\s*\n", content.strip())
#     concept_paragraphs = []

#     # Identify paragraphs with conceptual or vivid elements
#     for idx, para in enumerate(paragraphs):
#         if any(keyword in para.lower() for keyword in [
#             "data", "model", "training", "evaluation", "system", "architecture", 
#             "learning", "ai", "robot", "algorithm", "magic", "experiment"
#         ]):
#             concept_paragraphs.append((idx, para))

#     # Limit to 3 illustrations max
#     concept_paragraphs = concept_paragraphs[:3]

#     enhanced_parts = paragraphs.copy()
#     image_dir = "images"
#     os.makedirs(image_dir, exist_ok=True)

#     def save_image_and_return_markdown(img, idx):
#         """Save PIL image locally and return Markdown reference."""
#         filename = f"illustration_{idx}.png"
#         filepath = os.path.join(image_dir, filename)
#         img.save(filepath)
#         return f"![illustration]({filepath})"

#     # Generate and embed images inline
#     for idx, para in concept_paragraphs:
#         visual_prompt = (
#             f"Create an interactive, cartoon-style educational illustration inspired by this text:\n\n{para}\n\n"
#             "The image should feel imaginative, colorful, and story-like — no text labels, only visuals."
#         )
#         try:
#             image = client.text_to_image(
#                 visual_prompt,
#                 model="black-forest-labs/FLUX.1-dev"
#             )

#             image_markdown = save_image_and_return_markdown(image, idx)
#             enhanced_parts.insert(idx * 2 + 1, image_markdown)

#         except Exception as e:
#             enhanced_parts.insert(idx * 2 + 1, f"<!-- Error generating image: {e} -->")

#     # Combine paragraphs and images
#     state["enhanced_text"] = "\n\n".join(enhanced_parts)
#     print("🎨 Added 3 interactive cartoon-style illustrations inline (Markdown-compatible).")
#     return state
