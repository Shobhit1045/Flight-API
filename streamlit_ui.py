import streamlit as st
from hiting import hit
import json
st.title("Flight Bot")


if "greet" not in st.session_state:
    st.session_state.greet = []
if "conv1" not in st.session_state:
    st.session_state.conv1 = []
if "conv2" not in st.session_state:
    st.session_state.conv2 = []


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
    response=hit(prompt,st.session_state.greet,st.session_state.conv1,st.session_state.conv2,last2)
    print(response)
    json_obj = json.loads(response)
    assis=json_obj["response"]
    json=""
    try:
        json=json_obj["json"]
    except:
        json=""

    st.session_state.greet=json_obj["greet"]
    st.session_state.conv1=json_obj["conv1"]
    st.session_state.conv2=json_obj["conv2"]
    st.chat_message("assistant").markdown(assis)

    st.session_state.messages.append({"role": "assistant", "content": assis})
    if json!="":
        st.session_state.greet=[]
        st.session_state.conv1=[]
        st.session_state.conv2=[]
        st.write(json)
        print(json)
