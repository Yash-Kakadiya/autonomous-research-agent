import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.tools.retriever import create_retriever_tool

load_dotenv()


# 1. Structured Output Schema
class ResearchReport(BaseModel):
    executive_summary: str = Field(description="A high-level summary of the topic.")
    key_statistics: list[str] = Field(description="A list of 3 to 5 key data points.")
    sources_used: list[str] = Field(description="A list of sources referenced.")


# 2. RAG Pipeline
def process_document(file_path: str):
    """Loads a PDF, splits it, and creates a retriever tool."""
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2-preview",
        google_api_key=os.environ.get("GEMINI_API_KEY"),
    )
    vectorstore = FAISS.from_documents(splits, embeddings)
    retriever = vectorstore.as_retriever()

    retriever_tool = create_retriever_tool(
        retriever,
        "document_search",
        "Search through the uploaded document for relevant information. Use this when the user asks about the uploaded file.",
    )
    return retriever_tool


# 3. Agent Setup with Memory
def get_agent_executor(retriever_tool=None):
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash", google_api_key=os.environ.get("GEMINI_API_KEY")
    )

    search_tool = DuckDuckGoSearchRun()
    tools = [search_tool]
    if retriever_tool:
        tools.append(retriever_tool)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a highly capable AI research assistant. You have access to a web search tool and optionally a document search tool. Use them to answer questions accurately. If you don't know the answer, use your tools to find out.",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor


# 4. LCEL Pipeline for Structured Output
def generate_structured_report(chat_history_text: str) -> ResearchReport:
    """Takes raw chat text and forces it into the Pydantic schema using LCEL."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", google_api_key=os.environ.get("GEMINI_API_KEY")
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert editor. Extract the key information from the conversation below and format it perfectly according to the requested schema. If information is missing, return 'Not found'.",
            ),
            ("human", "{text}"),
        ]
    )

    structured_llm = llm.with_structured_output(ResearchReport)
    formatting_chain = prompt | structured_llm

    return formatting_chain.invoke({"text": chat_history_text})
