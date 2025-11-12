#!/usr/bin/env python3
"""
Quick test to run the workflow and inspect the returned state.
This helps diagnose why report content is not being populated.
Handles dict state returns from LangGraph.
"""

import json
import sys
import os
from Agent_workflow import graph

def test_workflow(arxiv_id: str = "2005.11401"):
    """Test the workflow with a specific ArXiv ID."""
    print(f"\n{'='*60}")
    print(f"Testing workflow with ArXiv ID: {arxiv_id}")
    print(f"{'='*60}\n")
    
    try:
        # Run the workflow
        print("🚀 Starting workflow execution...")
        final_state = graph.invoke(
            {"research_paper": arxiv_id},
            config={"recursion_limit": 25}
        )
        
        print("\n✅ Workflow completed successfully!\n")
        
        # Inspect the returned state
        print(f"{'='*60}")
        print("STATE INSPECTION RESULTS")
        print(f"{'='*60}\n")
        
        print("📋 Type of final_state:", type(final_state))
        print("\n📊 State field values:\n")
        
        # Check each important field
        important_fields = [
            'research_paper', 'title', 'pdf_path', 
            'text', 'summary_text', 'enhanced_text',
            'story_text', 'humor_text', 'domain_expert',
            'report', 'report_file', 
            'image_summary', 'methodology_summary',
            'last_feedback', 'loop_count', 'next_node'
        ]
        
        # Handle dict state from LangGraph
        if isinstance(final_state, dict):
            print("✅ State is a dictionary (expected from LangGraph.invoke())\n")
            for field_name in important_fields:
                if field_name in final_state:
                    value = final_state[field_name]
                else:
                    value = None
                    
                if value is None:
                    status = "❌ None"
                    preview = ""
                elif isinstance(value, str) and len(value) == 0:
                    status = "⚠️  Empty string"
                    preview = ""
                elif isinstance(value, str):
                    status = f"✅ String ({len(value)} chars)"
                    preview = f"\n   Preview: {value[:200]}..."
                else:
                    status = f"✅ {type(value).__name__}"
                    preview = f"\n   Value: {str(value)[:100]}..."
                
                print(f"  {field_name}: {status}{preview}\n")
        else:
            print("⚠️ State is NOT a dictionary. Processing as object.\n")
            for field_name in important_fields:
                if hasattr(final_state, field_name):
                    value = getattr(final_state, field_name)
                else:
                    value = None
                    
                if value is None:
                    status = "❌ None"
                    preview = ""
                elif isinstance(value, str) and len(value) == 0:
                    status = "⚠️  Empty string"
                    preview = ""
                elif isinstance(value, str):
                    status = f"✅ String ({len(value)} chars)"
                    preview = f"\n   Preview: {value[:200]}..."
                else:
                    status = f"✅ {type(value).__name__}"
                    preview = f"\n   Value: {str(value)[:100]}..."
                
                print(f"  {field_name}: {status}{preview}\n")
        
        # Try to read report from file if path exists
        print(f"\n{'='*60}")
        print("REPORT FILE INSPECTION")
        print(f"{'='*60}\n")
        
        # Handle both dict and object
        if isinstance(final_state, dict):
            report_path = final_state.get('report_file')
        else:
            report_path = getattr(final_state, 'report_file', None)
            
        if report_path:
            print(f"Report file path: {report_path}")
            
            if os.path.exists(report_path):
                print(f"✅ File exists!")
                try:
                    with open(report_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"\n📄 Report content ({len(content)} chars):")
                        print(f"\n{content[:800]}...\n")
                except Exception as e:
                    print(f"❌ Error reading file: {e}")
            else:
                print(f"❌ File does not exist at: {report_path}")
        else:
            print("❌ No report_file path found in state")
        
        # Save full state to JSON for inspection
        print(f"\n{'='*60}")
        print("SAVING FULL STATE TO JSON")
        print(f"{'='*60}\n")
        
        try:
            # Handle both dict and object state
            if isinstance(final_state, dict):
                state_dict = final_state
            elif hasattr(final_state, 'model_dump'):
                state_dict = final_state.model_dump()
            else:
                # Fallback for older Pydantic versions
                state_dict = final_state.dict()
            
            # Save to file
            with open('test_state_output.json', 'w', encoding='utf-8') as f:
                json.dump(state_dict, f, indent=2, default=str)
            
            print("✅ Full state saved to: test_state_output.json")
            print(f"\nKey fields in saved state:")
            for key in ['report', 'report_file', 'story_text', 'humor_text', 'enhanced_text', 'domain_expert']:
                if key in state_dict and state_dict[key]:
                    val_len = len(str(state_dict[key]))
                    print(f"  ✅ {key}: Present ({val_len} chars)")
                else:
                    print(f"  ❌ {key}: Missing or empty")
                    
        except Exception as e:
            print(f"❌ Error saving state: {e}")
        
        print(f"\n{'='*60}\n")
        
        return final_state
        
    except Exception as e:
        print(f"\n❌ Workflow failed with error:")
        print(f"\n{type(e).__name__}: {e}\n")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Allow passing ArXiv ID as command-line argument
    arxiv_id = sys.argv[1] if len(sys.argv) > 1 else "2005.11401"
    test_workflow(arxiv_id)
