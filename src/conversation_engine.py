import os
from llama_index.core import load_index_from_storage
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core import StorageContext
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import FunctionTool
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.agent.openai import OpenAIAgent
from datetime import datetime
import json
from src.global_settings import INDEX_STORAGE,SCORES_FILE,CONVERSATION_FILE
from src.prompts import CUSTOM_AGENT_SYSTEM_TEMPLATE
from llama_index.llms.openai import OpenAI
import openai
import chainlit as cl

user_avatar = "data/images/user.png"
professor_avatar = "data/images/professor.png"

# Function to initialize or reload the chat history.
def load_chat_store():
    if os.path.exists(CONVERSATION_FILE) and os.path.getsize(CONVERSATION_FILE) > 0:
        try:
            chat_store = SimpleChatStore.from_persist_path(CONVERSATION_FILE) # Load the chat store from the file
        except:
            chat_store = SimpleChatStore() # If there is an error, create a new chat store
    else:
        chat_store = SimpleChatStore()

    return chat_store


# Function to save the diagnostic results.
def save_score(score, content, total_guess, username):
        """Write score and content to a file.

        Args:
            score (string): Score of the user's mental health.
            content (string): Content of the user's mental health.
            total_guess (string): Total guess of the user's mental health.
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = {
            "username": username,
            "Time": current_time,
            "Score": score,
            "Content": content,
            "Total guess": total_guess
        }
        
        # Đọc dữ liệu từ file nếu tồn tại
        try:
            with open(SCORES_FILE, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        
        # Thêm dữ liệu mới vào danh sách
        data.append(new_entry)
        
        # Ghi dữ liệu trở lại file
        with open(SCORES_FILE, "w") as f:
            json.dump(data, f, indent=4)


# Function to create agent.
def initialize_chatbot(chat_store, container):
    memory = ChatMemoryBuffer.from_defaults(
        token_limit=3000,
        chat_store = chat_store,
        chat_store_key= "user"
    )

    storage_context = StorageContext.from_defaults(
        persist_dir=INDEX_STORAGE
    )

    index = load_index_from_storage(storage_context,index_id="vector")

    engine = index.as_query_engine(similarity_top_k=3),

    tool = QueryEngineTool(
        query_engine=engine,
        metadata=ToolMetadata(
            name="book",
            description= (
                f"Cung cấp thông tin từ văn bản lưu trữ của cuốn sách 'The Psychology of Money' của Morgan Housel. "
                f"Sử dụng câu hỏi văn bản thuần túy chi tiết làm đầu vào cho công cụ."
            )
        )
    )

    save_tool = FunctionTool.from_defaults(fn=save_score)
    agent = OpenAIAgent.from_tools(
        tools=[tool,save_tool],
        memory=memory,
        system_prompt=CUSTOM_AGENT_SYSTEM_TEMPLATE.format(user_info="Hai")
    )

    return agent

def chat_interface(agent, chat_store):
    if not os.path.exists(CONVERSATION_FILE) or os.path.getsize(CONVERSATION_FILE) == 0:
        cl.Message(
            content="Chào bạn, mình là Chatbot được phát triển bởi AI. Mình sẽ giúp bạn đưa ra những quyết định về tiền đúng đắn giúp tốt hơn cho sức khỏe tinh thần. Hãy nói chuyện với mình để bắt đầu.",
            role="assistant",
            avatar=professor_avatar
        )

    # Capture user input
    prompt = cl.text_input("Viết tin nhắn tại đây ạ...")

    if prompt:
        # Display user message
        cl.Message(content=prompt, role="user", avatar=user_avatar)

        # Get response from agent
        response = str(agent.chat(prompt))

        # Display assistant response
        cl.Message(content=response, role="assistant", avatar=professor_avatar)

        # Persist the chat history
        chat_store.persist(CONVERSATION_FILE)