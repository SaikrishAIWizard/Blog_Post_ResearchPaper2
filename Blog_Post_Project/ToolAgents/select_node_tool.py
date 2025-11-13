from langchain.tools import tool
from typing import Literal

@tool
def select_node(
    node_choice: Literal["domain_expert", "storytelling", "structured_narrative", "END"]
) -> str:
    """
    Select which node to revisit next in the workflow based on feedback.
    
    Args:
        node_choice: The next node to visit:
            - "domain_expert": Revisit domain expert structuring
            - "storytelling": Revisit storytelling
            - "structured_narrative": Revisit Narrative structure cohesion and transition quality
            - "END": End the workflow (draft is complete)
    
    Returns:
        Confirmation of the selected node
    """
    return f"Selected node: {node_choice}"
