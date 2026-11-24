from app.graph.workflow import flowmind_graph

def test_langgraph_workflow_execution():
    initial_state = {
        "user_id": 1,
        "query": "What unfinished activities do I have?",
        "engine_hint": "intent",
        "intent_detected": "pending",
        "memory_snapshot": {},
        "need_rag": False,
        "retrieved_docs": [],
        "need_tool": False,
        "tool_to_execute": None,
        "tool_input_args": {},
        "tool_execution_result": None,
        "tools_executed": [],
        "reasoning": "",
        "final_response": "",
        "memory_updates": {}
    }

    res = flowmind_graph.invoke(initial_state)
    assert res is not None
    assert res.get("intent_detected") == "intent_recovery"
    assert "final_response" in res
