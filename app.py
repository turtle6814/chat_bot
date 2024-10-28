import os
import openai
import chainlit as cl
from dotenv import load_dotenv
load_dotenv()
from literalai import LiteralClient
from typing import Dict, Optional

from llama_index.core import (
    Settings,
    StorageContext,
    VectorStoreIndex,
    SimpleDirectoryReader,
    load_index_from_storage,
)
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.query_engine.retriever_query_engine import RetrieverQueryEngine
from llama_index.core.callbacks import CallbackManager
from llama_index.core import Settings

literalai_client = LiteralClient(api_key=os.getenv("LITERAL_API_KEY"))

openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    # load index
    index = load_index_from_storage(storage_context)
except:
    documents = SimpleDirectoryReader("./data").load_data(show_progress=True)
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist()


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
    Settings.llm = OpenAI(
        model="gpt-4o-mini", temperature=0.2, max_tokens=1024, streaming=True
    )
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
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


@cl.on_message
async def main(message: cl.Message):
    query_engine = cl.user_session.get(
        "query_engine")  # type: RetrieverQueryEngine

    msg = cl.Message(content="", author="Assistant")

    res = await cl.make_async(query_engine.query)(message.content)

    for token in res.response_gen:
        await msg.stream_token(token)
    await msg.send()

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
