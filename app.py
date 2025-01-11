# Only for streamlit deployment
# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
#

import os

from autogen import AssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

import streamlit as st

gpt4o_llm_config = {
    "config_list": [{"model": "gpt-4o", "api_key": os.getenv("OPENAI_API_KEY")}],
    "timeout": 600,
    "temperature": 0.2,
    "cache_seed": 1234,
}

from autogen.retrieve_utils import TEXT_FORMATS
# print(TEXT_FORMATS)


def generate_response(problem):
    # 1. create an AssistantAgent instance named "assistant"

    assistant_system_message = """
    You are able to write code blocks in the chat based on the given Open API Specification to complete the given task.
    Your response must follow the following requirements:
    Rule 1: Your response must include both the explanation and the code blocks. 
    Rule 2: Your response must include the URL of any referenced API specification. 
    Rule 3: The response must be in a markdown format.
    Rule 4: The code block in your response must specify an object's data properties defined in the components section. 
    Rule 5: If you have to make an assumption, you must call it out in your response.
    Rule 6: If you can't find the answer in the API specification, please reply 'I can't find related information in the API specification'.
    """

    assistant = AssistantAgent(
        name="assistant",
        system_message=assistant_system_message,
        llm_config=gpt4o_llm_config,
    )

    # 2. create the RetrieveUserProxyAgent instance named "ragproxyagent"
    # Refer to https://microsoft.github.io/autogen/docs/reference/agentchat/contrib/retrieve_user_proxy_agent
    # and https://microsoft.github.io/autogen/docs/reference/agentchat/contrib/vectordb/mongodb
    # for more information on the RetrieveUserProxyAgent and MongoDBAtlasVectorDB
    rag_proxy_customized_prompt = """
    "You under the Open API specifications. 
     For a given task, You need to retrieve only the relevant API specifications from the database 
     and then provide them to the code writing agent.
     Do NOT retrieve all API specifications without understanding the given task first. 
    """

    ragproxyagent = RetrieveUserProxyAgent(
        name="ragproxyagent",
        retrieve_config={
            "task": "code",
            "docs_path": [
                # "https://developer.ferguson.com/sites/default/files/2021-05/Ferguson-API-API-Order-1.0.8-resolved.json",
                "https://developer.ferguson.com/sites/default/files/2024-09/Ferguson-API-Pricing-2.0.1_0.json",
                "https://developer.ferguson.com/sites/default/files/2024-09/Ferguson-API-inventoryCAC-1.0.1-resolved.yaml",
                "https://developer.ferguson.com/sites/default/files/2021-05/Ferguson-API-Products-1.0.12-resolved.json",
                # "https://developer.ferguson.com/sites/default/files/2021-05/Ferguson-API-API-Quote-1.0.5-resolved.json",
                "https://developer.ferguson.com/sites/default/files/2021-05/Ferguson-API-API-Location-2.0.0-resolved.json",
                # 
                # "https://raw.githubusercontent.com/jaredlang/sample-services/refs/heads/main/inventory/inventory-query-service-api-spec.yaml",
            ],
            "chunk_token_size": 2000,
            "model": gpt4o_llm_config["config_list"][0]["model"],
            "vector_db": "mongodb",  # MongoDB Atlas database
            "collection_name": "ferg_api_spec_collection",
            "db_config": {
                "connection_string": os.environ["MONGO_ATLAS_URI"],  # MongoDB Atlas connection string
                "database_name": "Cluster0",  # MongoDB Atlas database
                "index_name": "vector_index",
                "wait_until_index_ready": 120.0,  # Setting to wait 120 seconds or until index is constructed before querying
                "wait_until_document_ready": 120.0,  # Setting to wait 120 seconds or until document is properly indexed after insertion/update
            },
            "get_or_create": True,  # set to False if you don't want to reuse an existing collection
            "overwrite": False,  # set to True if you want to overwrite an existing collection, each overwrite will force a index creation and reupload of documents
        },
        human_input_mode="NEVER",
        # max_consecutive_auto_reply=10,
        code_execution_config=False,  # set to False if you don't want to execute the code,
    )

    # reset the assistant. Always reset the assistant before starting a new conversation.
    # assistant.reset()

    # given a problem, we use the ragproxyagent to generate a prompt to be sent to the assistant as the initial message.
    # the assistant receives the message and generates a response. The response will be sent back to the ragproxyagent for processing.
    # The conversation continues until the termination condition is met, in RetrieveChat, the termination condition when no human-in-loop is no code block detected.
    # With human-in-loop, the conversation will continue until the user says "exit".

    # RetrieveUserProxyAgent system message is empty!!! 
    print("RetrieveUserProxyAgent system message: ", ragproxyagent.system_message)
    print("RetrieveUserProxyAgent message_generator: ", ragproxyagent.message_generator)

    # initiate the chat with the assistant
    chat_result = ragproxyagent.initiate_chat(assistant, message=ragproxyagent.message_generator, problem=problem, max_turns=1, silent=False)

    response = chat_result.chat_history[-1]["content"]
    print(response)

    return response


def app():
    st.set_page_config(page_title="Ferguson API Chatbot", page_icon="🤖", layout="wide")
    st.header("Ferguson API Chatbot")

    with st.form("api_chatbot_form"):
        question = st.text_area(
            label="What can I help you with Ferguson APIs?",
            placeholder="For example, you can ask how to get a quote for a product.",
            value="Write a function to check the inventory and find all products with the quantity larger than 300"
        )
        submitted = st.form_submit_button("Submit")
        if submitted:
            response = generate_response(question)
            st.write(response)


if __name__ == "__main__":
    app()
