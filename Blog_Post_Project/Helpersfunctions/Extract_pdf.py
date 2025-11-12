import os
from models import PaperState
import fitz  # PyMuPDF
from Helpersfunctions.progress import append_progress


def extract_pdf_node(state: PaperState) -> PaperState:
    """Extract text and images from the PDF."""
    #pdf_path = state.get("pdf_path", None)
    pdf_path = state.pdf_path
    
    doc = fitz.open(pdf_path)
    text = ""
    # image_paths = []
    # os.makedirs("paper_images", exist_ok=True)

    for i, page in enumerate(doc):
        text += page.get_text("text")
        # for j, img in enumerate(page.get_images(full=True)):
        #     xref = img[0]
        #     pix = fitz.Pixmap(doc, xref)
        #     img_path = f"paper_images/page_{i+1}_img_{j+1}.png"
        #     if pix.n < 5:
        #         pix.save(img_path)
        #     else:
        #         pix = fitz.Pixmap(fitz.csRGB, pix)
        #         pix.save(img_path)
        #     image_paths.append(img_path)
    doc.close()

    state.text = text
    #state["images"] = image_paths
    msg = f"📄 Extracted text length: {len(text)}"
    print(msg)
    append_progress(msg)
    return state

