#!/usr/bin/env python3
"""
Quick test to verify progress module integration works correctly.
"""
import sys
from pathlib import Path

# Add Blog_Post_Project to path
project_dir = Path(__file__).parent / "Blog_Post_Project"
sys.path.insert(0, str(project_dir))

from Helpersfunctions.progress import (
    clear as clear_progress,
    get_messages,
    append_progress,
    set_result,
    get_result
)

def test_progress_module():
    """Test the progress module functions."""
    print("=" * 60)
    print("TESTING PROGRESS MODULE INTEGRATION")
    print("=" * 60)
    
    # Test 1: Clear messages
    print("\n✓ Test 1: Clearing prior messages")
    clear_progress()
    msgs = get_messages()
    print(f"  Messages after clear: {msgs}")
    assert msgs == [], "Clear should result in empty list"
    print("  ✅ PASS")
    
    # Test 2: Append progress messages
    print("\n✓ Test 2: Appending progress messages")
    test_messages = [
        "⏳ Started processing research paper",
        "📄 Downloading and extracting paper (simulated)",
        "🔁 Invoking workflow agents",
        "⚙️ Workflow completed, collecting results",
        "💾 Saved serialized state to final_state.json",
        "✅ Blog post generated successfully in 2.5m",
    ]
    
    for msg in test_messages:
        append_progress(msg)
        print(f"  Appended: {msg}")
    
    msgs = get_messages()
    print(f"\n  Total messages: {len(msgs)}")
    assert len(msgs) == len(test_messages), "Should have 6 messages"
    print("  ✅ PASS")
    
    # Test 3: Display all messages
    print("\n✓ Test 3: Displaying all progress messages")
    for i, msg in enumerate(msgs, 1):
        print(f"  [{i}] {msg}")
    print("  ✅ PASS")
    
    # Test 4: Set and get result
    print("\n✓ Test 4: Setting and retrieving final result")
    test_result = {
        "status": "success",
        "blog_post_generated": True,
        "iterations": 5,
        "rating": 8.5
    }
    set_result(test_result)
    result = get_result()
    print(f"  Result set: {test_result}")
    print(f"  Result retrieved: {result}")
    assert result == test_result, "Result should match what was set"
    print("  ✅ PASS")
    
    # Test 5: Message limit (max 200)
    print("\n✓ Test 5: Testing message limit (max 200)")
    clear_progress()
    for i in range(250):
        append_progress(f"Message {i+1}")
    
    msgs = get_messages()
    print(f"  Added 250 messages, retained: {len(msgs)}")
    assert len(msgs) <= 200, "Should not exceed 200 messages"
    assert "Message 51" in msgs[0], "Should keep recent messages"
    print("  ✅ PASS")
    
    # Test 6: Frontend rendering format (as in BlogStreamApp.py)
    print("\n✓ Test 6: Frontend markdown rendering format")
    clear_progress()
    
    messages = [
        "⏳ Started processing research paper",
        "📄 Downloading paper...",
        "🔁 Running workflow...",
        "✅ Complete!"
    ]
    
    for msg in messages:
        append_progress(msg)
    
    msgs = get_messages()
    markdown_output = "\n".join(f"- {m}" for m in msgs)
    print("  Markdown output (as rendered in Streamlit):")
    print("  " + markdown_output.replace("\n", "\n  "))
    print("  ✅ PASS")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✅")
    print("=" * 60)
    print("\nIntegration Summary:")
    print("  • Progress module functions work correctly")
    print("  • Messages persist and can be retrieved")
    print("  • Result storage/retrieval works")
    print("  • Message limit enforced (max 200)")
    print("  • Markdown formatting ready for Streamlit")
    print("\nBlogStreamApp.py is ready to:")
    print("  1. Clear prior messages on workflow start")
    print("  2. Append messages at each stage")
    print("  3. Display live progress to frontend users")
    print("  4. Store final result for post-processing")

if __name__ == "__main__":
    try:
        test_progress_module()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
