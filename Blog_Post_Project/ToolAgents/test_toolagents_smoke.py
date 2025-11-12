#!/usr/bin/env python3
"""
Smoke test for ToolAgents: call each tool node directly with a minimal fake state and
print the outputs so we can confirm they run and return the updated state.
"""
import os
import sys
from types import SimpleNamespace

# Ensure project root is on sys.path
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from ToolAgents.domain_expert_structuring_agent import domain_expert_structuring_tool_node
from ToolAgents.Storytelling_agent import storytelling_tool_node
from ToolAgents.Humor_agent import humor_tool_node


def make_state():
    # Minimal fake state object with attributes used by the tool agents
    s = SimpleNamespace()
    s.last_feedback = "Please make the explanation clearer and more engaging."
    s.report = "This is a short draft report about methodology."
    s.domain_expert = "AI"
    s.loop_count = 0
    s.report_file = "test_report.md"
    return s


def print_state(prefix, state):
    print(f"--- {prefix} ---")
    for k in ["report", "story_text", "humor_text", "domain_expert"]:
        val = getattr(state, k, None)
        if val is None:
            print(f"{k}: None")
        else:
            s_val = str(val)
            print(f"{k}: ({len(s_val)} chars) {s_val[:120]!r}")
    print()


def main():
    print("Running ToolAgents smoke test...\n")

    # Domain expert tool
    state1 = make_state()
    print("Calling domain_expert_structuring_tool_node...")
    out1 = domain_expert_structuring_tool_node(state1)
    if out1 is None:
        print("domain_expert_structuring_tool_node returned None\n")
    else:
        print_state("Domain Expert Output", out1)

    # Storytelling
    state2 = make_state()
    state2.report = out1.report if out1 is not None else state2.report
    print("Calling storytelling_tool_node...")
    out2 = storytelling_tool_node(state2)
    if out2 is None:
        print("storytelling_tool_node returned None\n")
    else:
        print_state("Storytelling Output", out2)

    # Humor
    state3 = make_state()
    state3.report = out2.report if out2 is not None else state3.report
    print("Calling humor_tool_node...")
    out3 = humor_tool_node(state3)
    if out3 is None:
        print("humor_tool_node returned None\n")
    else:
        print_state("Humor Output", out3)

if __name__ == '__main__':
    main()
