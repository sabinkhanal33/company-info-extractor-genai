# agent.py
from datetime import date
from typing import List
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from database import insert_company_data

@tool
def add_company_to_db(company_name: str, founding_date: date, founders: List[str]) -> str:
    """
    Adds a new company record to the PostgreSQL database.
    This tool should be used when company information has been extracted and is ready for storage.
    """
    return insert_company_data(company_name, founding_date, founders)

def create_agent_executor():
    """Creates an intelligent agent with the database tool."""
    print("🤖 Initializing agent...")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [add_company_to_db]
    # The agent uses the tools to handle database operations [cite: 21, 47]
    agent_executor = create_react_agent(llm, tools)
    print("✅ Agent is ready.")
    return agent_executor

def run_agent_to_add_company(agent_executor, company_info):
    """Invokes the agent to add a company to the database."""
    prompt = (
        f"A new company has been identified. Please add it to the database. "
        f"Company Name: {company_info.company_name}, "
        f"Founding Date: {company_info.founding_date}, "
        f"Founders: {company_info.founders}"
    )
    
    response = agent_executor.invoke({"messages": [HumanMessage(content=prompt)]})
    # The agent's final response will confirm the action
    final_message = response['messages'][-1].content
    print(f"🤖 Agent response: {final_message}")