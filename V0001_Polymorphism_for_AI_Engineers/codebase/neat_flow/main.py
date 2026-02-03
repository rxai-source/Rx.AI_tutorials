# neat_flow/main.py

import asyncio
from llms.registry import get_llm
from agent.agent import Agent

async def main():
    print(f"*****************Gemini Response*****************")
    llm = get_llm("gemini")
    agent = Agent(llm)

    await agent.run(
        "Polymorphism is great! I am going to use it for my Rx.AI YouTube video. Motivate me."
    )

    print("================================")

    print(f"*****************OpenRouter Nemotron Response*****************")

    llm = get_llm("openrouter")
    agent = Agent(llm)

    await agent.run(
        "Polymorphism is great! I am going to use it for my Rx.AI YouTube video. Motivate me."
    )

if __name__ == "__main__":
    asyncio.run(main())