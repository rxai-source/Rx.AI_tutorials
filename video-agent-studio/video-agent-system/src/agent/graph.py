from langgraph.graph import StateGraph, START, END
from src.agent.state import AgentState
from src.agent.nodes import AgentNodes 
from src.agent.orchestrator import Orchestrator
from src.agent.executor import Executor



def build_graph(
    orchestrator: Orchestrator | None = None,
    executor: Executor | None = None,
):
    """
    Build and compile the agent execution graph.

    Graph:

        START
          |
          v
    orchestrator
          |
          v
       executor
          |
          v
         END
    """
    #Define the graph using AgentState
    vid_gen_graph = StateGraph(AgentState)

    #Define an instance of Orchestrator, Executor agents
    orchestrator = orchestrator or Orchestrator()
    executor = executor or Executor()

    agent_nodes = AgentNodes(orchestrator=orchestrator, executor=executor)

    #Nodes
    vid_gen_graph.add_node("orchestrator",agent_nodes.orchestrator_node)
    vid_gen_graph.add_node("executor",agent_nodes.executor_node)

    #Edges
    vid_gen_graph.add_edge(START,"orchestrator")
    vid_gen_graph.add_conditional_edges(
        "orchestrator",
        lambda state: "executor" if state.get("execute_tasks", True) and state.get("task_queue") else END,
        {"executor": "executor", END: END},
    )
    vid_gen_graph.add_conditional_edges(
        "executor",
        lambda state: "executor" if state.get("task_queue") else END,
        {"executor": "executor", END: END},
    )

    return vid_gen_graph.compile()
