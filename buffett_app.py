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
column_list = ['CASH_AND_CASH_EQUIVALENTS','SHORT_TERM_INVESTMENTS','RECEIVABLES','INVENTORY','OTHER_CURRENT_ASSETS','TOTAL_CURRENT_ASSETS','PROPERTY_PLANT_AND_EQUIPMENT','GOODWILL','INTANGIBLE_ASSETS','ACCUMULATED_AMORTIZATION','OTHER_ASSETS','TOTAL_ASSETS','ACCOUNTS_PAYABLE_AND_ACCRUED_EXPENSES','SHORT_OR_CURRENT_LONG_TERM_DEBT','OTHER_CURRENT_LIABILITIES','TOTAL_CURRENT_LIABILITIES','LONG_TERM_DEBT','OTHER_LIABILITIES','DEFERRED_LONG_TERM_LIABILITY_CHARGES','MINORITY_INTEREST','NEGATIVE_GOODWILL','TOTAL_LIABILITIES','MISC_STOCKS_OPTIONS_WARRANTS','REDEEMABLE_PREFERRED_STOCK','PREFERRED_STOCK','COMMON_STOCK','RETAINED_EARNINGS','TREASURY_STOCK','CAPITAL_SURPLUS','OTHER_STOCKHOLDER_EQUITY','TOTAL_STOCKHOLDER_EQUITY','NET_TANGIBLE_ASSETS','NET_INCOME','DEPRECIATION','CHANGES_IN_ACCOUNTS_RECEIVABLES','CHANGES_IN_ASSETS_AND_LIABILITIES','CHANGES_IN_INVENTORIES','CHANGES_IN_OTHER_OPERATING_ACTIVITIES','TOTAL_CASH_FLOW_FROM_OPERATING_ACTIVITIES','CAPITAL_EXPENDITURES','INVESTMENTS','OTHER_CASH_FLOWS_FROM_INVESTING_ACTIVITIES','TOTAL_CASH_FLOWS_FROM_INVESTING_ACTIVITIES','DIVIDENDS_PAID','SALE_OR_PURCHASE_OF_STOCK','NET_BORROWINGS','OTHER_CASH_FLOWS_FROM_FINANCING_ACTIVITIES','TOTAL_CASH_FLOWS_FROM_FINANCING_ACTIVITIES','CHANGE_IN_CASH_AND_CASH_EQUIVALENTS','TOTAL_REVENUE','COST_OF_REVENUE','GROSS_PROFIT','RESEARCH_DEVELOPMENT','SELLING_GENERAL_AND_ADMINISTRATIVE','NON_RECURRING','OTHERS','TOTAL_OPERATING_EXPENSES','OPERATING_INCOME_OR_LOSS','TOTAL_OTHER_INCOME_OR_EXPENSES_NET','EARNINGS_BEFORE_INTEREST_AND_TAXES','INTEREST_EXPENSE','INCOME_BEFORE_TAX','INCOME_TAX_EXPENSE','MINORITY_INTEREST','NET_INCOME_FROM_CONTINUING_OPS','DISCONTINUED_OPERATIONS','EXTRAORDINARY_ITEMS','EFFECT_OF_ACCOUNTING_CHANGES','OTHER_ITEMS','NET_INCOME','PREFERRED_STOCK_AND_OTHER_ADJUSTMENTS','NET_INCOME_APPLICABLE_TO_COMMON_SHARES']
cutoff = 20
# establish snowpark connection
conn = st.experimental_connection("snowpark")


# adding this to test out caching
st.cache_data(ttl=86400)

# adding this to test out caching
st.cache_data(ttl=86400)

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
    new_image = image.resize((760, 100))
    st.image(new_image) 
    
    query = st.chat_input("Enter your question:")
    st.markdown("""
    **Empower non-technical users to derive insights from the knowledge base documents and collaterals stored in SharePoint and other knowledge repositories.**
          
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
