from huggingface_hub import HfApi
from dotenv import load_dotenv
import requests
load_dotenv()
import os, re, arxiv
from models import PaperState
from Helpersfunctions.progress import append_progress

os.environ["HF_TOKEN"]=os.getenv("HF_TOKEN")


def download_research_paper_node(state: PaperState) -> PaperState:
    """Download a research paper from Hugging Face Papers API and Arxiv."""
    api = HfApi(token=os.environ["HF_TOKEN"])
    arxiv_pattern = re.compile(r'^\d{4}\.\d{5}$')  # matches typical Arxiv IDs like '2510.02350'

    #research_paper = state.get("research_paper", "AI")
    research_paper = state.research_paper
    if research_paper and arxiv_pattern.match(research_paper):
        paper_id = research_paper
        print(f"Research paper {research_paper} identified as Arxiv ID.")
        append_progress("Identified ArXiv ID: %s" % research_paper)
    else:       
        papers = api.list_papers(query=research_paper)

        for paper in papers:
            print("Evaluating Paper:",paper)
            paper_id = getattr(paper, 'id', None)
            summary = getattr(paper, 'summary', None) 
            upvotes = getattr(paper, 'upvotes', None)
            image = getattr(paper, 'thumbnail', None)
            title = getattr(paper, 'title', None)
            print("Paper Details:",paper)

            print(f"ID: {paper_id}")
            print(f"Title: {title}")
            print(f"Summary: {summary}")
            print(f"Upvotes Count: {upvotes}")
            print(f"Image URL: {image}")
            print('---')
            if paper_id and arxiv_pattern.match(paper_id):
                print(f"Paper {paper_id} is from Arxiv. Breaking.")
                break

    # Arxiv document ID
    arxiv_id = paper_id

    # Search for the paper by id
    search = arxiv.Search(id_list=[arxiv_id])
    print(search.results())

    # Get the paper result
    paper = next(search.results())

    # Print paper metadata
    print("Title:", paper.title)
    print("Authors:", [author.name for author in paper.authors])
    print("Published:", paper.published)
    print("Summary:", paper.summary)

    # Ensure output directory exists
    os.makedirs("ResearchPapers", exist_ok=True)

    # Robust PDF download: construct URL from arxiv_id and use requests
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    print(f"\n📥 Using constructed URL: {pdf_url}")

    out_path = os.path.join("ResearchPapers", f"research_paper.pdf")
    try:
        resp = requests.get(pdf_url, stream=True, timeout=30)
        resp.raise_for_status()
        with open(out_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"✅ Downloaded PDF as {arxiv_id}.pdf")
        print(f"    (Downloaded via direct URL)")
        append_progress(f"Downloaded the Research Paper")
    except Exception as e:
        print(f"❌ Direct download failed ({e})")
        print("🔄 Attempting fallback with arxiv library...")
        try:
            paper.download_pdf(filename=out_path)
            print(f"✅ Downloaded PDF as {arxiv_id}.pdf (via arxiv library)")
        except Exception as fallback_e:
            print(f"❌ Fallback also failed: {fallback_e}")
            raise
        # Download the PDF of the paper (saved to the current directory)
        paper.download_pdf(filename=f"ResearchPapers/{arxiv_id}.pdf")
    state.title = paper.title
    state.pdf_path = f"ResearchPapers/research_paper.pdf"
    print(f"Downloaded PDF as research_paper.pdf")
    append_progress(f"Paper metadata extracted: {paper.title}")
    return state

