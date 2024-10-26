import os
import openai
from dotenv import load_dotenv
load_dotenv()
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, Document
from llama_index.core import Settings
from llama_index.core import load_index_from_storage
from llama_index.core.tools import QueryEngineTool, ToolMetadata, FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgent

from src.prompts import CUSTOM_AGENT_SYSTEM_TEMPLATE

openai.api_key = os.getenv("OPENAI_API_KEY")
Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.2)

try:
    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    # load index
    index = load_index_from_storage(storage_context)
except:
    documents = SimpleDirectoryReader("./data/ingestion_storage").load_data(show_progress=True)
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist()

query_engine = index.as_query_engine(
    similarity_top_k=3
)

# function tools
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
        f"Cung cấp thông tin từ văn bản lưu trữ của cuốn sách 'The Psychology of Money' của Morgan Housel. "
        f"Sử dụng câu hỏi văn bản thuần túy chi tiết làm đầu vào cho công cụ."
    ),
)

agent = OpenAIAgent.from_tools([multiply_tool, add_tool, tool], system_prompt=CUSTOM_AGENT_SYSTEM_TEMPLATE, verbose=True)

while True:
    text_input = input("User: ")
    if text_input == "exit":
        break
    response = agent.chat(text_input)
    print(f"Agent: {response}")
