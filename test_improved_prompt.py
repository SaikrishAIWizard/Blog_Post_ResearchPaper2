#!/usr/bin/env python3
"""
Test script to demonstrate improved LLM evaluation prompt with structured feedback.
Shows sample outputs for different scenarios.
"""

import re
from typing import Tuple

def extract_numeric_rating(text: str) -> float:
    """Extract numeric rating from LLM response."""
    if not text:
        return 0.0
    m = re.search(r"\b(10|[1-9])(?:\s*/\s*10)?\b", str(text))
    if m:
        try:
            return float(m.group(1))
        except Exception:
            return 0.0
    return 0.0


def parse_structured_feedback(feedback_text: str) -> Tuple[str, str]:
    """Extract specific issues and action items from structured feedback."""
    specific_issues = "No specific issues identified."
    action_items = "Continue with next improvement phase."
    
    if "SPECIFIC_ISSUES:" in feedback_text:
        try:
            issues_start = feedback_text.index("SPECIFIC_ISSUES:") + len("SPECIFIC_ISSUES:")
            issues_end = feedback_text.index("ACTION_ITEMS:") if "ACTION_ITEMS:" in feedback_text else len(feedback_text)
            specific_issues = feedback_text[issues_start:issues_end].strip()
        except Exception:
            pass
    
    if "ACTION_ITEMS:" in feedback_text:
        try:
            actions_start = feedback_text.index("ACTION_ITEMS:") + len("ACTION_ITEMS:")
            action_items = feedback_text[actions_start:].strip()
        except Exception:
            pass
    
    return specific_issues, action_items


# Sample LLM responses with the new prompt format
SAMPLE_RESPONSES = [
    # Sample 1: Domain expert needs improvement
    """RATING: 6
FEEDBACK: The blog post covers the main concepts of the research paper but lacks depth in technical explanations. The writing is clear, and the humor is well-placed, but readers may not fully grasp the methodology.
IMPROVEMENT_TARGET: domain_expert
SPECIFIC_ISSUES:
- Methodology section is too brief and skips key algorithmic details
- Mathematical notation explained poorly, needs more intuitive examples
- Missing connection between theory and practical applications
ACTION_ITEMS:
- Expand methodology section with step-by-step algorithm breakdown
- Add concrete numerical examples for mathematical concepts
- Include real-world use cases and applications
- Ensure technical terms are properly defined""",
    
    # Sample 2: Storytelling needs improvement
    """RATING: 7
FEEDBACK: The technical content is accurate and comprehensive. Humor elements are present. However, the narrative flow feels disconnected—paragraphs don't transition smoothly, and the overall story arc lacks engagement.
IMPROVEMENT_TARGET: storytelling
SPECIFIC_ISSUES:
- Abrupt transitions between concepts make the blog feel disjointed
- Opening hook is weak, doesn't capture reader interest
- Conclusion doesn't tie back to the main narrative thread
ACTION_ITEMS:
- Restructure paragraphs to create smooth thematic transitions
- Rewrite opening with a compelling hook or relatable example
- Add narrative bridges that connect each section
- Create a stronger conclusion that summarizes the key narrative arc""",
    
    # Sample 3: Humor needs improvement
    """RATING: 8
FEEDBACK: Excellent technical depth and narrative structure. The domain expertise is evident, and the story flows naturally. However, the humor feels forced and doesn't add value—some jokes are inappropriate for the academic audience.
IMPROVEMENT_TARGET: humor
SPECIFIC_ISSUES:
- Jokes feel out of place and break the professional tone
- Sarcasm is too heavy-handed and may alienate readers
- Some cultural references may not resonate with international audience
ACTION_ITEMS:
- Replace forced jokes with subtle, intelligent humor
- Use wit that demonstrates domain expertise (technical humor)
- Include light analogies that clarify concepts without being cartoonish
- Remove any references that assume specific cultural background""",
    
    # Sample 4: Blog is complete
    """RATING: 9
FEEDBACK: Excellent work! The blog post demonstrates comprehensive domain knowledge, exceptional storytelling with smooth transitions, and appropriate humor that enhances rather than distracts. The writing is accessible to both technical and non-technical audiences. This draft is publication-ready.
IMPROVEMENT_TARGET: END
SPECIFIC_ISSUES:
- None identified. The blog post meets all quality standards.
ACTION_ITEMS:
- Blog post is ready for publication
- Consider submitting to academic blogging platforms
- Share with target audience for final feedback""",
]


def demonstrate_evaluation(response_text: str, scenario: str) -> None:
    """Demonstrate the evaluation process."""
    print("\n" + "="*80)
    print(f"SCENARIO: {scenario}")
    print("="*80)
    
    print("\n📝 LLM RESPONSE:")
    print("-" * 80)
    print(response_text)
    print("-" * 80)
    
    # Extract rating
    rating = extract_numeric_rating(response_text)
    print(f"\n⭐ Rating: {rating}/10")
    
    # Extract structured feedback
    specific_issues, action_items = parse_structured_feedback(response_text)
    
    print(f"\n🔍 Specific Issues:")
    for line in specific_issues.split('\n'):
        if line.strip():
            print(f"   {line}")
    
    print(f"\n✅ Action Items:")
    for line in action_items.split('\n'):
        if line.strip():
            print(f"   {line}")
    
    # Determine next node
    if "END" in response_text:
        next_node = "END"
        print(f"\n✨ Decision: Blog post is COMPLETE - No further improvements needed")
    elif "domain_expert" in response_text:
        next_node = "domain_expert"
        print(f"\n🎯 Next Node: domain_expert → Will enhance technical depth and accuracy")
    elif "storytelling" in response_text:
        next_node = "storytelling"
        print(f"\n🎯 Next Node: storytelling → Will improve narrative flow and structure")
    elif "humor" in response_text:
        next_node = "humor"
        print(f"\n🎯 Next Node: humor → Will refine humor quality and appropriateness")
    else:
        next_node = "generate_report"
        print(f"\n🎯 Next Node: generate_report → Default next action")
    
    # Comprehensive feedback summary
    feedback_summary = (
        f"📊 Rating: {rating}/10 | 🎯 Next: {next_node}\n"
        f"🔍 Specific Issues:\n{specific_issues}\n"
        f"✅ Action Items:\n{action_items}"
    )
    print(f"\n💾 State Update - last_tool_feedback:")
    print("-" * 80)
    print(feedback_summary)
    print("-" * 80)


def main():
    print("\n" + "="*80)
    print("IMPROVED LLM EVALUATION PROMPT - DEMONSTRATION")
    print("="*80)
    print("""
This demonstrates the enhanced tool_calling_llm() function that:
1. Extracts precise RATING (1-10)
2. Parses SPECIFIC_ISSUES affecting quality
3. Provides ACTIONABLE FEEDBACK for improvement agents
4. Routes to appropriate next node: domain_expert | storytelling | humor | END

The new prompt format ensures:
✓ Structured feedback that's easy to parse
✓ Specific improvement guidance for each agent
✓ Clear decision logic for node routing
✓ Better feedback in the frontend UI
""")
    
    # Run demonstrations
    for i, response in enumerate(SAMPLE_RESPONSES, 1):
        scenarios = [
            "Domain Expertise Needs Improvement",
            "Story Structure Needs Improvement",
            "Humor Quality Needs Improvement",
            "Blog Post is Complete & Publication-Ready"
        ]
        demonstrate_evaluation(response, scenarios[i-1])
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("""
✅ IMPROVEMENTS MADE:

1. ENHANCED SYSTEM MESSAGE:
   - Explains evaluator role more clearly
   - Sets expectations for structured feedback
   - Emphasizes critical but constructive approach

2. IMPROVED USER MESSAGE:
   - Requests evaluation across 4 dimensions:
     * Domain accuracy & technical correctness
     * Story coherence & narrative flow
     * Humor quality & appropriateness
     * Overall readability & accessibility
   
   - Specifies EXACT output format with sections:
     * RATING: [number]
     * FEEDBACK: [detailed critique]
     * IMPROVEMENT_TARGET: [selected node]
     * SPECIFIC_ISSUES: [2-3 specific problems]
     * ACTION_ITEMS: [concrete suggestions]

3. BETTER PARSING LOGIC:
   - Extracts specific_issues and action_items from response
   - More robust error handling
   - Structured feedback available in state.last_tool_feedback

4. IMPROVED STATE UPDATES:
   - state.last_tool_feedback now contains:
     * Rating: X/10
     * Selected node: domain_expert | storytelling | humor | END
     * Specific issues identified
     * Concrete action items for improvement agents

5. FRONTEND DISPLAY:
   - Users see clear feedback on what needs improvement
   - Each agent gets specific guidance on what to fix
   - Progress messages include actionable insights

🎯 EXPECTED OUTCOMES:

- LLM provides more precise feedback
- Improvement agents know exactly what to focus on
- Frontend users understand why nodes were selected
- Better quality blog posts through iterative refinement
- Clearer decision-making at each evaluation loop
""")


if __name__ == "__main__":
    main()
