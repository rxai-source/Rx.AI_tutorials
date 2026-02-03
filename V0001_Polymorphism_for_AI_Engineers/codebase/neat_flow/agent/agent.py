# neat_flow/agent/agent.py

from llms.base import BaseLLM

class Agent:
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    async def run(self, prompt: str) -> None:
        response = await self.llm.generate_text(prompt)
        print(response)