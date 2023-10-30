import snowflake.connector
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import prompts
from tabulate import tabulate
from PIL import Image
from streamlit_option_menu import option_menu
from io import StringIO
from load.letter_load import operation

st.set_page_config(layout="wide")

username=st.secrets["streamlit_username"]
password=st.secrets["streamlit_password"]


def creds_entered():
    if len(st.session_state["streamlit_username"])>0 and len(st.session_state["streamlit_password"])>0:
          if  st.session_state["streamlit_username"].strip() != username or st.session_state["streamlit_password"].strip() != password: 
              st.session_state["authenticated"] = False
              st.error("Invalid Username/Password ")

          elif st.session_state["streamlit_username"].strip() == username and st.session_state["streamlit_password"].strip() == password:
              st.session_state["authenticated"] = True


def authenticate_user():
      if "authenticated" not in st.session_state:
        buff, col, buff2 = st.columns([1,1,1])
        col.text_input(label="Username:", value="", key="streamlit_username", on_change=creds_entered) 
        col.text_input(label="Password", value="", key="streamlit_password", type="password", on_change=creds_entered)
        return False
      else:
           if st.session_state["authenticated"]: 
                return True
           else:  
                  buff, col, buff2 = st.columns([1,1,1])
                  col.text_input(label="Username:", value="", key="streamlit_username", on_change=creds_entered) 
                  col.text_input(label="Password:", value="", key="streamlit_password", type="password", on_change=creds_entered)
                  return False

if authenticate_user():
    with st.sidebar:
      image = Image.open("assets/JadeLogo.png")
      image = st.image('assets/JadeLogo.png',width=250)
      image = Image.open("assets/KBSIDE.png")
      image = st.image('assets/KBSIDE.png',width=265)
   
    image = Image.open("assets/KB_Top.png")
    new_image = image.resize((830, 100))
    st.image(new_image) 
    
    query = st.chat_input("Enter your question:")
    st.markdown("""
    ##### Empower non-technical users to derive insights from the knowledge base documents and collaterals stored in SharePoint and other knowledge repositories.
          
    Some Sample Queries:
  
    - What is the Monitor and validate operational quality?
    - What is the difference between Traditional process and DevOps process?


    **Click button below to embed recently received additional KB material received on MLOps**
    
    """)
    
    st.button(label = "Embed MLOps document", on_click = operation )
    
    # Create a text input to edit the selected question
    if "messages_1" not in st.session_state.keys():
          st.session_state.messages_1 = []

    for message in st.session_state.messages_1:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html = True)
    
    if prompt1 := query:
        st.chat_message("user").markdown(prompt1, unsafe_allow_html = True)
          # Add user message to chat history
        st.session_state.messages_1.append({"role": "user", "content": prompt1})
        try:
            with st.chat_message("assistant"):
              result = prompts.letter_chain(query)
              st.write(result['result'])
              st.session_state.messages_1.append({"role": "assistant", "content":result['result'] } )

        except:
            st.write("Please try to improve your question")
