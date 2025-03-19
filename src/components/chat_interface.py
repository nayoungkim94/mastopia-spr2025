import streamlit as st
from datetime import datetime
import pytz
import time
from typing import Generator
from langchain_core.messages import HumanMessage


def display_chat_history(messages: list):
    for message in messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

def create_stop_button():
    col1, col2 = st.columns([0.9, 0.1])
    with col2:
        return st.button("🟥", help='Stop Generation')

def response_generator(response: str) -> Generator[str, None, None]:
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.05)


def render_chat_interface(session_manager, activity_logger):
    # Display chat history
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


    # Stop generation button
    if "stop_generation" not in st.session_state:
        st.session_state.stop_generation = False


    if prompt := st.chat_input("Message MASTOPIA"):
        user_timestamp = datetime.now(pytz.timezone('MST'))  # Record the timestamp in MST

        history = [msg for msg in st.session_state.messages if msg["role"] in ("user", "assistant")]            
        input_message = {"input": [HumanMessage(content=prompt)], "history" : history}

        st.session_state.stop_generation = False

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.markdown(prompt)
            with col2:
                if st.button("🟥", help='Stop Generation'):
                    st.session_state.stop_generation = True
        # Execute the graph with the input message
        result_generator = st.session_state.graph_model.execute(input_message)
        

        # for response in result_dict:
        #     print(response)
        #     if st.session_state.stop_generation:
        #         activity_logger.save_activity(st.session_state.user_id, {"user_activity": "click_stop_generation_button"})
        #         assistant_reply += " [Stopped]"
        #         break

        #     if isinstance(response, str):
        #         print("=")
        #         assistant_reply = response
        #         break

        #     elif isinstance(response, dict):
        #         for key, value in response.items():
        #             print("==")
        #             if key == "final_output":
        #             # if key != "Supervisor":
        #                 # output = value.get("output", "")
        #                 output = value
        #                 if isinstance(output, str):
        #                     assistant_reply = output
        #                 elif isinstance(output, list) and output:
        #                     assistant_reply = output[0].content
        #                 break
        
        # if not assistant_reply:
        #     assistant_reply = "Sorry, I didn't understand that."



        try:
            # Extract the assistant's reply
            assistant_reply = ""
            for response in result_generator:
                if st.session_state.stop_generation:
                    activity_logger.save_activity(st.session_state.user_id, {"user_activity": "click_stop_generation_button"})
                    assistant_reply += " [Stopped]"
                    break

                if "__end__" not in response and assistant_reply == "":
                    for agent, value in response.items():
                        if 'output' in value: 
                            output = value["output"]

                            if isinstance(output, str):
                                assistant_reply = value["output"]
                            else:
                                assistant_reply += value["output"][0].content
                        
            if assistant_reply == "":
                assistant_reply = "Sorry, I didn't understand that."

        except:
            assistant_reply = "Sorry, there was a problem with the response generation. Please try again. If this problem persists, try rephrasing your question or starting a new session."



        # Display assistant's message in chat message container
        with st.chat_message("assistant"):
        
            response = st.write_stream(response_generator(assistant_reply))
            assistant_reply_timestamp = datetime.now(pytz.timezone('MST'))  # Record the timestamp in MST


        # Add assistant's message to chat history
        st.session_state.messages.append({"role": "assistant", "content": response}) # "content": assistant_reply

        

        # Save activity to JSON file
        activity_logger.save_activity(st.session_state.user_id, {"user_activity": "chat_input",
                                        "user_message": prompt,
                                        "user_timestamp":user_timestamp,
                                        "assistant_reply": assistant_reply,
                                        "reply_timestamp": assistant_reply_timestamp.strftime("%Y-%m-%d_%H:%M:%S"),
                                        })