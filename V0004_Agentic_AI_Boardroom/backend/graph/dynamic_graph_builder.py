import sys
from typing import Callable, Dict, Any

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage

from core.templates.loader import RoomTemplate, RoomStage
from graph.state import DynamicRoomState


def _create_stage_node(stage: RoomStage, template: RoomTemplate) -> Callable[[DynamicRoomState], Dict[str, Any]]:
    """
    Factory function to create a LangGraph node function for a specific stage.
    Instantiates a DynamicAgent for the lead_agent and executes it.
    """
    # Find the persona config for this stage's lead agent
    persona = next((p for p in template.personas if p.id == stage.lead_agent), None)
    if not persona:
        raise ValueError(f"Persona '{stage.lead_agent}' not found in template personas.")

    async def dynamic_stage_node(state: DynamicRoomState) -> Dict[str, Any]:
        frame = sys._getframe()
        print(f"[DEBUG] {__file__}:{frame.f_lineno} | Executing stage: '{stage.id}' (Lead Agent: {stage.lead_agent})")
        
        # Lazy import to avoid circular dependencies if any
        from agents.dynamic_agent import DynamicAgent
        from llms.registry import get_llm
        
        llm = get_llm("gemini")
        agent = DynamicAgent(persona_config=persona, llm=llm)
        
        # Execute the agent
        stage_context = f"Stage Name: {stage.name}\nDescription: {stage.description}"
        print(f"[DEBUG] {__file__}:{frame.f_lineno} | Invoking DynamicAgent '{agent.name}'...")
        
        result = await agent.execute(state, stage_context)
        
        message_content = f"[{stage.name}] phase executed successfully by {stage.lead_agent}. Output snippet: {result['output'][:50]}..."
        print(f"[DEBUG] {__file__}:{frame.f_lineno} | {message_content}")
        
        return {
            "current_stage": stage.id,
            "messages": [AIMessage(content=result['output'], name=stage.lead_agent)],
            "status": "active"
        }
        
    # Rename the function dynamically for LangGraph debugging clarity
    dynamic_stage_node.__name__ = f"node_{stage.id}"
    return dynamic_stage_node


def build_dynamic_graph(template: RoomTemplate):
    """
    Compiles a LangGraph state machine dynamically based on the loaded template's stages.
    Returns the compiled graph.
    """
    frame = sys._getframe()
    print(f"[DEBUG] {__file__}:{frame.f_lineno} | Building dynamic graph for template: '{template.id}'")
    
    # Initialize the StateGraph with the isolated DynamicRoomState
    builder = StateGraph(DynamicRoomState)
    
    if not template.stages:
        print(f"[DEBUG] {__file__}:{frame.f_lineno} | WARNING: No stages found in template '{template.id}'")
        return builder.compile()

    # 1. Add nodes for each stage in the configuration
    for stage in template.stages:
        print(f"[DEBUG] {__file__}:{frame.f_lineno} | Registering node for stage: '{stage.id}'")
        node_func = _create_stage_node(stage, template)
        builder.add_node(stage.id, node_func)
        
    # 2. Add Entry Point (START -> First Stage)
    first_stage_id = template.stages[0].id
    print(f"[DEBUG] {__file__}:{frame.f_lineno} | Setting START edge to: '{first_stage_id}'")
    builder.add_edge(START, first_stage_id)
    
    # 3. Add Edges (Linear progression for now)
    # The Orchestrator will later introduce conditional routing here.
    for i in range(len(template.stages) - 1):
        current_stage = template.stages[i].id
        next_stage = template.stages[i+1].id
        print(f"[DEBUG] {__file__}:{frame.f_lineno} | Adding edge: '{current_stage}' -> '{next_stage}'")
        builder.add_edge(current_stage, next_stage)
        
    # 4. Add Exit Point (Last Stage -> END)
    last_stage_id = template.stages[-1].id
    print(f"[DEBUG] {__file__}:{frame.f_lineno} | Setting END edge from: '{last_stage_id}'")
    builder.add_edge(last_stage_id, END)
    
    compiled_graph = builder.compile()
    print(f"[DEBUG] {__file__}:{frame.f_lineno} | Successfully compiled dynamic graph for '{template.id}'")
    
    return compiled_graph
