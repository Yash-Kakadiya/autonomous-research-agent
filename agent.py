import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

class ResearchReport(BaseModel):
    executive_summary: str = Field(description="A high-level summary of the research topic.")
    key_statistics: list[str] = Field(description="A list of 3 to 5 key data points or statistics found during the search.")
    sources_used: list[str] = Field(description="A list of specific entities, websites, or sources referenced.")

def run_research(topic: str) -> ResearchReport:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
    search_tool = DuckDuckGoSearchRun()
    tools = [search_tool]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a professional market researcher. You use the provided search tool to find the latest information on a topic."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=5)
    
    raw_result = agent_executor.invoke({"input": f"Research this topic thoroughly: {topic}"})
    agent_output = raw_result.get("output", "")
    
    struct_prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract the information from the following research text and format it perfectly according to the schema. If information is missing, do your best to infer or return 'Not found'."),
        ("human", "{text}")
    ])
    
    structured_llm = llm.with_structured_output(ResearchReport)
    formatting_chain = struct_prompt | structured_llm
    
    final_report = formatting_chain.invoke({"text": agent_output})
    return final_report
