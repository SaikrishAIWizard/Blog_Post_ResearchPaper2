from typing import List, Optional
from langchain_core.messages import AnyMessage
from pydantic import BaseModel


class PaperState(BaseModel):
    research_paper: str
    text: Optional[str] = None
    summary_text: Optional[str] = None
    image_summary: Optional[str] = None
    report_file: Optional[str] = None
    story_text: Optional[str] = None
    humor_text: Optional[str] = None
    enhanced_text: Optional[str] = None
    title: Optional[str] = None
    pdf_path: Optional[str] = None
    research_paper_domain: Optional[str] = None
    last_feedback: Optional[str] = None
    reader_rating: Optional[float] = None
    next_node: Optional[str] = None
    loop_count: Optional[int] = 0
    methodology_summary: Optional[str] = None
    last_tool_feedback: Optional[str] = None
    report: Optional[str] = None
    domain_expert: Optional[str] = None
    messages: Optional[List[AnyMessage]] = None
