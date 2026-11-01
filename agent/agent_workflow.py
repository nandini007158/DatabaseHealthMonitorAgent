from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from database.monitor import (
    run_health_check,
    investigate_active_queries
)

from ai.ai_analyzer import analyze_database_health


# 1. Define the information shared between agent nodes
class AgentState(TypedDict):
    metrics: dict
    health_score: int
    overall_health: str
    problems: list
    root_causes: list
    active_queries: list
    ai_analysis: str


# 2. Monitor the MySQL database
def monitor_database(state: AgentState):

    print("\n[AGENT] Monitoring MySQL database...")

    report = run_health_check()

    return {
        "metrics": report["metrics"],
        "health_score": report["health_score"],
        "overall_health": report["overall_health"],
        "problems": report["problems"],
        "root_causes": report["root_causes"]
    }


# 3. Decide the next step
def decide_next_step(state: AgentState):

    if state["problems"]:
        print("\n[DECISION] Problems detected.")
        return "investigate"

    print("\n[DECISION] No problems detected.")
    return "healthy"


# 4. Investigate active MySQL queries
def investigate_database(state: AgentState):

    print("\n[AGENT] Starting deeper database investigation...")

    queries = investigate_active_queries()

    print("\n[AGENT] Query investigation completed.")

    return {
        "active_queries": queries
    }


# 5. Analyze a healthy database
def analyze_healthy_database(state: AgentState):

    print("\n[AGENT] Database is healthy. Preparing AI analysis...")

    return analyze_database(state)


# 6. Analyze database using Ollama
def analyze_database(state: AgentState):

    print("\n[AGENT] Sending database findings to local AI...")

    # Add investigation results to the metrics
    metrics = state["metrics"].copy()
    metrics["active_query_investigation"] = state.get(
        "active_queries", []
    )

    analysis = analyze_database_health(
        state["problems"],
        state["health_score"],
        metrics
    )

    return {
        "ai_analysis": analysis
    }


# 7. Build the LangGraph workflow
workflow = StateGraph(AgentState)

workflow.add_node("monitor", monitor_database)
workflow.add_node("investigate", investigate_database)
workflow.add_node("healthy", analyze_healthy_database)
workflow.add_node("analyze", analyze_database)

workflow.add_edge(START, "monitor")

workflow.add_conditional_edges(
    "monitor",
    decide_next_step,
    {
        "investigate": "investigate",
        "healthy": "healthy"
    }
)

workflow.add_edge("investigate", "analyze")
workflow.add_edge("healthy", END)

workflow.add_edge("analyze", END)


# 8. Compile the agent
agent = workflow.compile()


# 9. Run the complete agent
def run_agent():

    print("\n======================================")
    print(" AUTONOMOUS DATABASE HEALTH AGENT")
    print("======================================")

    initial_state = {
        "metrics": {},
        "health_score": 0,
        "overall_health": "",
        "problems": [],
        "root_causes": [],
        "active_queries": [],
        "ai_analysis": ""
    }

    result = agent.invoke(initial_state)

    print("\n========== FINAL AGENT REPORT ==========")

    print("Database Health:", result["overall_health"])
    print("Health Score:", result["health_score"], "/ 100")

    print("\nDetected Problems:")
    print(result["problems"])

    print("\nActive Query Investigation:")
    print(result["active_queries"])

    print("\nAI ANALYSIS:")
    print(result["ai_analysis"])

    print("\nAgent execution completed.")
    print("========================================")


if __name__ == "__main__":
    run_agent()