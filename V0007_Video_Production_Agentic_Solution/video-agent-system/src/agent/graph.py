from langgraph.graph import StateGraph, START, END
from src.agent.state import AgentState
from src.agent.nodes import AgentNodes 
from src.agent.orchestrator import Orchestrator
from src.agent.executor import Executor



def build_graph():
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
    orchestrator = Orchestrator()
    executor = Executor()

    agent_nodes = AgentNodes(orchestator=orchestrator,executor=executor)

    #Nodes
    vid_gen_graph.add_node("orchestrator",agent_nodes.orchestrator_node)
    vid_gen_graph.add_node("executor",agent_nodes.executor_node)

    #Edges
    vid_gen_graph.add_edge("START","orchestrator")
    vid_gen_graph.add_edge("orchestrator","executor")
    vid_gen_graph.add_edge("executor","END")

    return vid_gen_graph.compile()