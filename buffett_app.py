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
#column_list = ['CASH_AND_EQUIVALENTS','SHORT_TERM_INVESTMENTS','CASH_AND_SHORT_TERM_INVESTMENTS','RECEIVABLES','INVENTORY','TOTAL_CURRENT_ASSETS','PROPERTY_PLANT_EQUIPMENTNET','GOODWILL','INTANGIBLE_ASSETS','GOOD_WILL_AND_INTANGIBLE_ASSETS','LONG_TERM_INVESTMENTS','TAX_ASSETS','OTHER_NON_CURRENT_ASSETS','TOTAL_NON_CURRENT_ASSETS','OTHER_ASSETS','TOTAL_ASSETS','ACCOUNTS_PAYABLES','SHORT_TERM_DEBT','TAX_PAYABLES','OTHER_CURRENT_LIABILITIES','TOTAL_CURRENT_LIABILITIES','LONG_TERM_DEBT','DEFERRED_REVENUE_NONCURRENT','DEFERRED_TAX_LIABILITIES_NONCURRENT','OTHER_NONCURRENT_LIABILITIES','TOTAL_LIABILITIES','RETAINED_EARNINGS','ACCUMULATED_OTHER_COMPREHENSIVE_INCOME','OTHER_TOTAL_STOCKHOLDERS_EQUIT','TOTAL_STOCKHOLDERS_EQUITY','TOTAL_EQUITY','TOTAL_LIABILITIES_AND_STOCKHOLDERS_EQUITY','MINORITY_INTEREST','TOTAL_LIABILITIES_AND_TOTAL_EQUITY','TOTAL_INVESTMENTS','TOTAL_DEBT','NET_DEBT','NET_INCOME','DEPRECIATION_AND_AMORTIZATION','DEFERRED_INCOME_TAX','STOCK_BASED_COMPENSATION','CHANGE_IN_WORKING_CAPITAL','ACCOUNTS_RECEIVABLES','INVENTORY','ACCOUNTS_PAYABLES','OTHER_WORKING_CAPITAL','OTHER_NON_CASH_ITEMS','NET_OPERATING_ACTIVITIES','INVESTMENTS_IN_PROPERTY_PLANT_AND_EQUIPMENT','ACQUISITIONS','PURCHASES_OF_INVESTMENTS','SALES_OF_INVESTMENTS','OTHER_INVESTING_ACTIVITES','NET_INVESTING_ACTIVITES','DEBT_PAYMENT','COMMON_STOCK_ISSUED','COMMON_STOCK_REPURCHASED','DIVIDENDS_PAID','OTHER_FINANCING_ACTIVITES','NET_FINANCING_ACTIVITIES','NET_CHANGE_IN_CASH','OPERATING_CASH_FLOW','CAPITAL_EXPENDITURE','FREE_CASH_FLOW','REVENUE','COST_OF_REVENUE','GROSS_PROFIT','GROSS_PROFIT_RATIO','RESEARCH_AND_DEVELOPMENT_EXPENSES','SELLING_GENERAL_AND_ADMINISTRATIVE_EXPENSES','OPERATING_EXPENSES','COST_AND_EXPENSES','INTEREST_INCOME','INTEREST_EXPENSE','DEPRECIATION_AND_AMORTIZATION','EBITDA_EARNINGS_BEFORE_INTEREST_TAX_DEPRECATION_AND_AMORITZATION','OPERATING_INCOME','OTHER_INCOME_EXPENSES','INCOME_BEFORE_TAX','INCOME_TAX_EXPENSE','NET_INCOME','EPS_EARNINGS_PER_SHARE','EPS_EARNINGS_PER_SHARE_DILUTED','WEIGHTED_AVERAGE_SHARES_OUTSTANDING','WEIGHTED_AVERAGE_SHARES_OUTSTANDING_DILUTED']
column_list = ['CASH_AND_CASH_EQUIVALENTS','SHORT_TERM_INVESTMENTS','RECEIVABLES','INVENTORY','OTHER_CURRENT_ASSETS','TOTAL_CURRENT_ASSETS','PROPERTY_PLANT_AND_EQUIPMENT','GOODWILL','INTANGIBLE_ASSETS','ACCUMULATED_AMORTIZATION','OTHER_ASSETS','TOTAL_ASSETS','ACCOUNTS_PAYABLE_AND_ACCRUED_EXPENSES','SHORT_OR_CURRENT_LONG_TERM_DEBT','OTHER_CURRENT_LIABILITIES','TOTAL_CURRENT_LIABILITIES','LONG_TERM_DEBT','OTHER_LIABILITIES','DEFERRED_LONG_TERM_LIABILITY_CHARGES','MINORITY_INTEREST','NEGATIVE_GOODWILL','TOTAL_LIABILITIES','MISC_STOCKS_OPTIONS_WARRANTS','REDEEMABLE_PREFERRED_STOCK','PREFERRED_STOCK','COMMON_STOCK','RETAINED_EARNINGS','TREASURY_STOCK','CAPITAL_SURPLUS','OTHER_STOCKHOLDER_EQUITY','TOTAL_STOCKHOLDER_EQUITY','NET_TANGIBLE_ASSETS','NET_INCOME','DEPRECIATION','CHANGES_IN_ACCOUNTS_RECEIVABLES','CHANGES_IN_ASSETS_AND_LIABILITIES','CHANGES_IN_INVENTORIES','CHANGES_IN_OTHER_OPERATING_ACTIVITIES','TOTAL_CASH_FLOW_FROM_OPERATING_ACTIVITIES','CAPITAL_EXPENDITURES','INVESTMENTS','OTHER_CASH_FLOWS_FROM_INVESTING_ACTIVITIES','TOTAL_CASH_FLOWS_FROM_INVESTING_ACTIVITIES','DIVIDENDS_PAID','SALE_OR_PURCHASE_OF_STOCK','NET_BORROWINGS','OTHER_CASH_FLOWS_FROM_FINANCING_ACTIVITIES','TOTAL_CASH_FLOWS_FROM_FINANCING_ACTIVITIES','CHANGE_IN_CASH_AND_CASH_EQUIVALENTS','TOTAL_REVENUE','COST_OF_REVENUE','GROSS_PROFIT','RESEARCH_DEVELOPMENT','SELLING_GENERAL_AND_ADMINISTRATIVE','NON_RECURRING','OTHERS','TOTAL_OPERATING_EXPENSES','OPERATING_INCOME_OR_LOSS','TOTAL_OTHER_INCOME_OR_EXPENSES_NET','EARNINGS_BEFORE_INTEREST_AND_TAXES','INTEREST_EXPENSE','INCOME_BEFORE_TAX','INCOME_TAX_EXPENSE','MINORITY_INTEREST','NET_INCOME_FROM_CONTINUING_OPS','DISCONTINUED_OPERATIONS','EXTRAORDINARY_ITEMS','EFFECT_OF_ACCOUNTING_CHANGES','OTHER_ITEMS','NET_INCOME','PREFERRED_STOCK_AND_OTHER_ADJUSTMENTS','NET_INCOME_APPLICABLE_TO_COMMON_SHARES']
columns_to_keep = ['TICKER','YEAR','CALENDAR_YEAR','PERIOD','PERIOD_ENDING']
cutoff = 20
# establish snowpark connection
conn = st.experimental_connection("snowpark")

# Reset the connection before using it if it isn't healthy
try:
    query_test = conn.query('select 1')
except:
    conn.reset()

# adding this to test out caching
st.cache_data(ttl=86400)

# def convert_to_numeric(value):
#     try:
#         return float(value)
#     except ValueError:
#         return value
        

def plot_financials(df_2, x, y, x_cutoff, title):
    """"
    helper to plot the altair financial charts
    
    return st.altair_chart(alt.Chart(df_2.head(x_cutoff)).mark_bar().encode(
        x=x,
        y=y
        ).properties(title=title)
    ) 
    """
   
    df = pd.DataFrame(df_2)
    return st.bar_chart(data=df,x=df.columns[0], y=df.columns[1:], color=None,width=0, height=300, use_container_width=True) 
       
       
def fs_chain(str_input):
    """
    performs qa capability for a question using sql vector db store
    the prompts.fs_chain is used but with caching
    """
    output = prompts.fs_chain(str_input)
    type(output)
    return output

# adding this to test out caching
st.cache_data(ttl=86400)
def sf_query(str_input):
    """
    performs snowflake query with caching
    """
    data = conn.query(str_input)
    return data

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
      image = Image.open("assets/FinGPT.png")
      image = st.image('assets/FinGPT.png',width=280)
      selected = option_menu( menu_title="Explore",
      menu_icon = "search",
      options=['Annual Reports'], 
      icons=['filetype-pdf'],  
      default_index=0,
      styles={#"container":{"font-family": "Garamond"},
        "nav-link": {"font-family": "Source Sans Pro"},"font-size": "12px", "text-align": "left", "margin":"0px", "--hover-color": "grey"})
      #styles={"container":{"font-family": "Source Sans Pro"},
       # "nav-link": {"font-size": "12px", "text-align": "left", "margin":"0px", "--hover-color": "grey"}})
    if selected =='Annual Reports':
        query = st.chat_input("Enter your question:")
        st.markdown("""

        I am capable of reviewing the annual reports from 2019 to 2021. Please ask me questions and I will try my level best to provide accurate responses.
              
        **Some Sample Questions:**
      
        - What was the net income of Marvell in 2019?
        - What was the receivables of Marvell in 2020?
        
        """)
        
        st.button(label = "Press the button for 2022 data", on_click = operation )
        
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
