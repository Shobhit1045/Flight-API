import streamlit as st
from hiting import hit
import json
from datetime import datetime
st.title("Flight Bot")


# if "greet" not in st.session_state:
#     st.session_state.greet = []

# if "conv2" not in st.session_state:
#     st.session_state.conv2 = []


if "session_id" not in st.session_state:
    st.session_state.session_id = f"{datetime.now()}"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "You can book a flight"}]
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    st.chat_message(message["role"]).markdown(message["content"])

cnt=0
# React to user input
if prompt := st.chat_input("Hii dbot here to code"):

    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    last2=st.session_state.messages[-2:]
    # non_mandatory_json={}
    response=hit(prompt,st.session_state.session_id)
    print(response)
    json_obj = json.loads(response)
    assis=json_obj["response"]
    st.chat_message("assistant").markdown(assis)
    st.session_state.messages.append({"role": "assistant", "content": assis})

