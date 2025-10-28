'''
agent to talk and send gmail and invites
'''

from langchain.agents import create_agent
from my_tools import get_tools, get_my_own_tools
from config import SYSTEM_PROMPT, system_prompt
from langchain_google_genai import ChatGoogleGenerativeAI
from copy import deepcopy

# from langgraph.checkpoint.memory import MemorySaver


from langchain_openai import ChatOpenAI

my_tools = get_my_own_tools()

# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
llm = ChatOpenAI(name="gpt-4o-mini")

# Use Gemini model with Gmail/Calendar tools
agent = create_agent(
    model=llm,
    tools=my_tools,
    system_prompt=SYSTEM_PROMPT,
)
