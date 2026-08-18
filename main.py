from dotenv import load_dotenv
load_dotenv()

import asyncio
from agent import Agent
asyncio.run(Agent.start())
