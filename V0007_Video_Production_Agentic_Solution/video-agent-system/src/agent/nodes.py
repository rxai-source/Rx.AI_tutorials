from src.agent.state import AgentState
from src.agent.orchestrator import Orchestrator
from src.agent.executor import Executor

class AgentNodes:
    def __init__(self,orchestator: Orchestrator, executor:Executor):
        self.orchestator = orchestrator
        self.executor = executor

    async def orchestrator_node(self,state:AgentState):
        #The orchestrator node in the graph gets the plan from the Orchestrator agent
        plan = await self.orchestator.create_plan(user_input=state.get("user_input","missing user_input"))
        return  {"task_list":plan.tasks}

    async def executor_node(self,state:AgentState):
        #The executor receives the tasks and sends them to the executor agent
        results = await self.executor.execute(tasks=state.get("tasks","missing tasks"))
        #It returns the results from the executor agent
        return {"results" : results}
