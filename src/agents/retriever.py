import functools
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain.tools.retriever import create_retriever_tool
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI

def agent_node(state, agent, name):
    result = agent.invoke(state)
    return {"output": [HumanMessage(content=result["output"], name=name)]}

def get_agent(retriever):
    llm = ChatOpenAI(
                openai_api_key=st.session_state.config.openai['api_key'],
                model=st.session_state.config.get_model_config(st.session_state.version)['name'],
                temperature=st.session_state.config.get_model_config(st.session_state.version)['temperature']
            )        
    
    retriever_tool = create_retriever_tool(retriever, st.session_state.config.get_retriever_config(st.session_state.version)['tool_name'], st.session_state.config.get_retriever_config(st.session_state.version)['tool_description'])
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", st.session_state.retriever_prompt + st.session_state.mast_prompt),
            MessagesPlaceholder(variable_name="input"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_tools_agent(llm, [retriever_tool], prompt)
    executor = AgentExecutor(agent=agent, tools=[retriever_tool])

    retrieval_node = functools.partial(agent_node, agent=executor, name="Retriever")
    
    return retrieval_node