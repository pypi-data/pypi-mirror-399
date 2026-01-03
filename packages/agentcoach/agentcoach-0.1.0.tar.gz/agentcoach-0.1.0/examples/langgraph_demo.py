"""LangGraph demo with QualityGuardNode integration."""

from typing import Any, TypedDict

# Mock LangGraph components for demo
class StateGraph:
    """Mock StateGraph for demo."""
    def __init__(self, state_schema: type) -> None:
        self.nodes: dict = {}
        self.edges: list = []
        self.state_schema = state_schema
    
    def add_node(self, name: str, func: Any) -> None:
        self.nodes[name] = func
    
    def add_edge(self, from_node: str, to_node: str) -> None:
        self.edges.append((from_node, to_node))
    
    def set_entry_point(self, node: str) -> None:
        self.entry = node
    
    def set_finish_point(self, node: str) -> None:
        self.finish = node
    
    def compile(self) -> "CompiledGraph":
        return CompiledGraph(self)


class CompiledGraph:
    """Mock compiled graph."""
    def __init__(self, graph: StateGraph) -> None:
        self.graph = graph
    
    def invoke(self, state: dict) -> dict:
        """Execute graph (simplified)."""
        current_state = state.copy()
        
        # Execute nodes in order
        for node_name in ["retrieval", "tool", "draft_answer", "quality_guard"]:
            if node_name in self.graph.nodes:
                func = self.graph.nodes[node_name]
                current_state = func(current_state)
        
        return current_state


# State definition
class AgentState(TypedDict):
    """Agent state."""
    input: str
    retrieved_docs: list[dict]
    tool_results: list[dict]
    draft_answer: str
    final_answer: str
    quality_check: dict


# Mock nodes
def retrieval_node(state: AgentState) -> AgentState:
    """Mock retrieval node."""
    print("📚 Retrieving documents...")
    state["retrieved_docs"] = [
        {"id": "doc1", "content": "Python is a high-level programming language."},
        {"id": "doc2", "content": "Python was created by Guido van Rossum in 1991."},
    ]
    return state


def tool_node(state: AgentState) -> AgentState:
    """Mock tool node."""
    print("🔧 Executing tools...")
    state["tool_results"] = [
        {"tool": "search", "result": "Python 3.12 released in October 2023"},
    ]
    return state


def draft_answer_node(state: AgentState) -> AgentState:
    """Generate draft answer."""
    print("✍️  Generating draft answer...")
    
    # Intentionally create an answer without proper structure
    state["draft_answer"] = "Python is a programming language created by Guido van Rossum."
    state["final_answer"] = state["draft_answer"]
    
    return state


# Main demo
def main() -> None:
    """Run LangGraph demo with quality guard."""
    from agentcoach.langgraph import QualityGuardNode
    
    print("🎯 LangGraph Demo with AgentCoach Quality Guard\n")
    
    # Create quality guard with schema requirement
    quality_guard = QualityGuardNode(
        contract_schema={
            "type": "object",
            "required": ["answer", "confidence", "citations"],
            "properties": {
                "answer": {"type": "string"},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "citations": {"type": "array"},
            },
        },
        auto_repair=True,
    )
    
    # Build graph
    graph = StateGraph(AgentState)
    
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("tool", tool_node)
    graph.add_node("draft_answer", draft_answer_node)
    graph.add_node("quality_guard", quality_guard)
    
    graph.set_entry_point("retrieval")
    graph.add_edge("retrieval", "tool")
    graph.add_edge("tool", "draft_answer")
    graph.add_edge("draft_answer", "quality_guard")
    graph.set_finish_point("quality_guard")
    
    app = graph.compile()
    
    # Run graph
    print("🚀 Running agent workflow...\n")
    
    initial_state: AgentState = {
        "input": "Tell me about Python programming language",
        "retrieved_docs": [],
        "tool_results": [],
        "draft_answer": "",
        "final_answer": "",
        "quality_check": {},
    }
    
    result = app.invoke(initial_state)
    
    # Display results
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    
    print(f"\n📝 Draft Answer:\n{result['draft_answer']}\n")
    print(f"✅ Final Answer:\n{result['final_answer']}\n")
    
    quality = result["quality_check"]
    print(f"🎯 Quality Check:")
    print(f"  Passed: {quality['passed']}")
    if quality.get("errors"):
        print(f"  Errors: {quality['errors']}")
    if quality.get("warnings"):
        print(f"  Warnings: {quality['warnings']}")
    
    print("\n" + "="*60)
    print("✨ Notice how the quality guard automatically repaired")
    print("   the output to match the required JSON schema!")
    print("="*60)


if __name__ == "__main__":
    main()
