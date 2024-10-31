from llama_index.core import Settings
from llama_index.core.callbacks import CallbackManager
from llama_index.core.query_engine.retriever_query_engine import RetrieverQueryEngine
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core import (
    Settings,
    StorageContext,
    VectorStoreIndex,
    SimpleDirectoryReader,
    load_index_from_storage,
)
from typing import Dict, Optional
from literalai import LiteralClient
import os
import openai
import chainlit as cl
from dotenv import load_dotenv
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.agent.openai import OpenAIAgent
from src.prompts import CUSTOM_AGENT_SYSTEM_TEMPLATE
from langchain.memory import ConversationBufferMemory
from chainlit.types import ThreadDict
load_dotenv()


literalai_client = LiteralClient(api_key=os.getenv("LITERAL_API_KEY"))

openai.api_key = os.getenv("OPENAI_API_KEY")
Settings.llm = OpenAI(
    model="gpt-4o-mini", temperature=0.2, max_tokens=1024, streaming=True
)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

try:
    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    # load index
    index = load_index_from_storage(storage_context)
except:
    documents = SimpleDirectoryReader(
        "./data/ingestion_storage").load_data(show_progress=True)
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist()

query_engine = index.as_query_engine(
    similarity_top_k=3
)

# Agent chatbot


def multiply(a: float, b: float) -> float:
    """Multiply two numbers and returns the product"""
    return a * b


multiply_tool = FunctionTool.from_defaults(fn=multiply)


def add(a: float, b: float) -> float:
    """Add two numbers and returns the sum"""
    return a + b


add_tool = FunctionTool.from_defaults(fn=add)

tool = QueryEngineTool.from_defaults(
    query_engine,
    name="book",
    description=(
        f"Provide information about the book Recipes from My Home Kitchen from Christine Ha"
    ),
)

agent = OpenAIAgent.from_tools(
    [multiply_tool, add_tool, tool], system_prompt=CUSTOM_AGENT_SYSTEM_TEMPLATE, verbose=True)


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Morning routine ideation",
            message="Can you help me create a personalized morning routine that would help increase my productivity throughout the day? Start by asking me about my current habits and what activities energize me in the morning.",
            icon="./public/idea.svg",
        ),

        cl.Starter(
            label="Explain superconductors",
            message="Explain superconductors like I'm five years old.",
            icon="./public/learn.svg",
        ),
        cl.Starter(
            label="Python script for daily email reports",
            message="Write a script to automate sending daily email reports in Python, and walk me through how I would set it up.",
            icon="./public/terminal.svg",
        ),
        cl.Starter(
            label="Text inviting friend to wedding",
            message="Write a text asking a friend to be my plus-one at a wedding next month. I want to keep it super short and casual, and offer an out.",
            icon="./public/pen.svg",
        )
    ]


@cl.on_chat_start
async def start():
    Settings.context_window = 4096

    Settings.callback_manager = CallbackManager(
        [cl.LlamaIndexCallbackHandler()])
    query_engine = index.as_query_engine(
        streaming=True, similarity_top_k=3)
    cl.user_session.set("query_engine", query_engine)

    app_user = cl.user_session.get("user")
    # await cl.Message(
    #     author="Assistant", content="Hello! Im an AI assistant. How may I help you?"
    # ).send()

    # Memory for resume chat
    cl.user_session.set(
        "memory", ConversationBufferMemory(return_messages=True))


@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    memory = ConversationBufferMemory(return_messages=True)
    root_messages = [m for m in thread["steps"] if m["parentId"] == None]
    for message in root_messages:
        if message["type"] == "user_message":
            memory.chat_memory.add_user_message(message["output"])
        else:
            memory.chat_memory.add_ai_message(message["output"])

    cl.user_session.set("memory", memory)


@cl.step(type="tool")
async def call_tool(message):
    response = agent.chat(message)
    return str(response)


@cl.on_message
async def run_conversation(message: cl.Message):
    # message_history = cl.user_session.get("message_history")
    # message_history.append({"name": "user", "role": "user", "content": message.content})
    memory = cl.user_session.get("memory")  # type: ConversationBufferMemory

    answer = await call_tool(message.content)
    res = cl.Message(content=answer, author="Answer")

    await res.send()

    memory.chat_memory.add_user_message(message.content)
    memory.chat_memory.add_ai_message(res.content)


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None


@cl.header_auth_callback
def header_auth_callback(headers: Dict) -> Optional[cl.User]:
    # Verify the signature of a token in the header (ex: jwt token)
    # or check that the value is matching a row from your database
    if headers.get("test-header") == "test-value":
        return cl.User(identifier="admin", metadata={"role": "admin", "provider": "header"})
    else:
        return None


@cl.oauth_callback
def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: Dict[str, str],
    default_user: cl.User,
) -> Optional[cl.User]:
    return default_user
