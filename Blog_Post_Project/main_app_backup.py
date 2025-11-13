import json
from Agent_workflow import graph

# ---------- Step 6: Run the StateGraph ----------
user_input = input("Enter the research paper topic or Arxiv ID: ")

final_state = graph.invoke({"research_paper": user_input},
                           config={"recursion_limit":20,}
                           )

# ---------- Step 7: Save Final State as JSON ----------
output_file = "final_state.json"
try:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_state, f, ensure_ascii=False, indent=2)
    print(f"\n🧾 Final state saved successfully as '{output_file}'.")
except Exception as e:
    print(f"⚠️ Error saving final state: {e}")

# ---------- Step 8: Display Summary ----------
print("\n🎯 Pipeline complete.")
print(f"📘 Final report generated: {final_state.get('report_file', 'No report file found')}")
print(f"💬 Reader Feedback: {final_state.get('reader_feedback', 'No feedback available')}")
print(f"⭐ Rating: {final_state.get('reader_rating', 'N/A')}/10")
print(f"🧩 Next Suggested Node: {final_state.get('next_node', 'N/A')}")
