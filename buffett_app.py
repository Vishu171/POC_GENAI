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

st.set_page_config(layout="wide")

username=st.secrets["streamlit_username"]
password=st.secrets["streamlit_password"]
column_list = ['CASH_AND_CASH_EQUIVALENTS','SHORT_TERM_INVESTMENTS','RECEIVABLES','INVENTORY','OTHER_CURRENT_ASSETS','TOTAL_CURRENT_ASSETS','PROPERTY_PLANT_AND_EQUIPMENT','GOODWILL','INTANGIBLE_ASSETS','ACCUMULATED_AMORTIZATION','OTHER_ASSETS','TOTAL_ASSETS','ACCOUNTS_PAYABLE_AND_ACCRUED_EXPENSES','SHORT_OR_CURRENT_LONG_TERM_DEBT','OTHER_CURRENT_LIABILITIES','TOTAL_CURRENT_LIABILITIES','LONG_TERM_DEBT','OTHER_LIABILITIES','DEFERRED_LONG_TERM_LIABILITY_CHARGES','MINORITY_INTEREST','NEGATIVE_GOODWILL','TOTAL_LIABILITIES','MISC_STOCKS_OPTIONS_WARRANTS','REDEEMABLE_PREFERRED_STOCK','PREFERRED_STOCK','COMMON_STOCK','RETAINED_EARNINGS','TREASURY_STOCK','CAPITAL_SURPLUS','OTHER_STOCKHOLDER_EQUITY','TOTAL_STOCKHOLDER_EQUITY','NET_TANGIBLE_ASSETS','NET_INCOME','DEPRECIATION','CHANGES_IN_ACCOUNTS_RECEIVABLES','CHANGES_IN_ASSETS_AND_LIABILITIES','CHANGES_IN_INVENTORIES','CHANGES_IN_OTHER_OPERATING_ACTIVITIES','TOTAL_CASH_FLOW_FROM_OPERATING_ACTIVITIES','CAPITAL_EXPENDITURES','INVESTMENTS','OTHER_CASH_FLOWS_FROM_INVESTING_ACTIVITIES','TOTAL_CASH_FLOWS_FROM_INVESTING_ACTIVITIES','DIVIDENDS_PAID','SALE_OR_PURCHASE_OF_STOCK','NET_BORROWINGS','OTHER_CASH_FLOWS_FROM_FINANCING_ACTIVITIES','TOTAL_CASH_FLOWS_FROM_FINANCING_ACTIVITIES','CHANGE_IN_CASH_AND_CASH_EQUIVALENTS','TOTAL_REVENUE','COST_OF_REVENUE','GROSS_PROFIT','RESEARCH_DEVELOPMENT','SELLING_GENERAL_AND_ADMINISTRATIVE','NON_RECURRING','OTHERS','TOTAL_OPERATING_EXPENSES','OPERATING_INCOME_OR_LOSS','TOTAL_OTHER_INCOME_OR_EXPENSES_NET','EARNINGS_BEFORE_INTEREST_AND_TAXES','INTEREST_EXPENSE','INCOME_BEFORE_TAX','INCOME_TAX_EXPENSE','MINORITY_INTEREST','NET_INCOME_FROM_CONTINUING_OPS','DISCONTINUED_OPERATIONS','EXTRAORDINARY_ITEMS','EFFECT_OF_ACCOUNTING_CHANGES','OTHER_ITEMS','NET_INCOME','PREFERRED_STOCK_AND_OTHER_ADJUSTMENTS','NET_INCOME_APPLICABLE_TO_COMMON_SHARES']
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

def plot_financials(df_2, x, y, x_cutoff, title):
    """"
    helper to plot the altair financial charts
   
    return st.altair_chart(alt.Chart(df_2.head(x_cutoff)).mark_bar().encode(
        x=x,
        y=y
        ).properties(title=title)
    ) 
  """ 
    df_2 = pd.DataFrame(df_2)
    #st.write("Function-",df_2)
    df_subset = df_2.head(x_cutoff)
  
    # Create a bar chart using st.bar_chart()

    return st.bar_chart(df_subset.set_index(x))

    
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
      options=["Company Statements", 'Annual Reports'], 
      icons=['database', 'filetype-pdf'],  
      default_index=0,
      styles={"container":{"font-family": "Garamond"},
        "nav-link": {"font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "grey"}})
    if selected =='Company Statements':
        str_input = st.chat_input("Enter your question:")
        st.markdown("""
        I am  Finance Assistant of your company. I possess the ability to extract information from your company's financial statements like balance sheet, income statements, etc spanning across 2003 to 2022. Please ask me questions and I will try my level best to provide accurate responses.
          
      
          **Some Sample Questions:**
      
          - What is the net income of Marvell in 2022?
          - What is the gross profit in last 3 years?
        
        
        """)
        
        if "messages" not in st.session_state.keys():
              st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                role = message["role"]
                df_str = message["content"]
                if role == "user":
                    st.markdown(message["content"], unsafe_allow_html = True)
                    continue
                csv = StringIO(df_str)
                df_data = pd.read_csv(csv, sep=',')
                #st.write("Function2-",df_data)
                col1, col2 = st.columns(2)
                df_data.columns = df_data.columns.str.replace('_', ' ')
                headers = df_data.columns
                
                with col1:
                    st.markdown(tabulate(df_data, tablefmt="html",headers=headers,showindex=False), unsafe_allow_html = True)
                    #st.write(df_str)
                    
                    if len(df_data.index) >2 & len(df_data.columns) == 2:
                        y = list(df_data.columns[1:])
                        title_name = df_data.columns[0]+'-'+df_data.columns[1]
                        with col2:
                            plot_financials(df_data,df_data.columns[0],y, cutoff,title_name)
        
        if prompt := str_input:
            st.chat_message("user").markdown(prompt, unsafe_allow_html = True)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            try:
                output = fs_chain(str_input)
                #st.write(output['result'])
                try:
                    # if the output doesn't work we will try one additional attempt to fix it
                    query_result = sf_query(output['result'])
                    if len(query_result) >= 1:
                      with st.chat_message("assistant"):
                        df_2 = pd.DataFrame(query_result)
                        for name in df_2.columns:
                            if name in column_list:
                                new_name = f"{name} ($ millions)"
                                df_2.rename(columns={name : new_name}, inplace=True)
                        
                            #st.bar_chart(df_2) 
                        col1, col2 = st.columns(2)
                        df_2.columns = df_2.columns.str.replace('_', ' ')
                        headers = df_2.columns
                        with col1:
                         st.markdown(tabulate(df_2, tablefmt="html",headers=headers,showindex=False), unsafe_allow_html = True) 
                         
                        if len(df_2.index) >2 & len(df_2.columns) == 2:
                            y = list(df_2.columns[1:])
                            title_name = df_2.columns[0]+'-'+df_2.columns[1]
                            with col2:
                                plot_financials(df_2,df_2.columns[0],y, cutoff,title_name)
                             #st.write(df_2)
                      #st.session_state.messages.append({"role": "assistant", "content": tabulate(df_2, tablefmt="html",headers=headers,showindex=False)})
                        st.session_state.messages.append({"role": "assistant", "content": df_2.to_csv(sep=',', index=False)})
                        
                    else:
                      with st.chat_message("assistant"):
                        st.write("Please try to improve your question. Note this tab is for financial statement questions. Use Tab 2 to ask from Annual Reports .")
      
                except:                   
                      #st.session_state.messages.append({"role": "assistant", "content": "The first attempt didn't pull what you were needing. Trying again..."})
                      output = fs_chain(f'You need to fix the code but ONLY produce SQL code output. If the question is complex, consider using one or more CTE. Examine the DDL statements and answer this question: {output}')
                      st.write(sf_query(output['result']))
            except:
              with st.chat_message("assistant"):
                st.markdown("Please try to improve your question. Note this tab is for financial statement questions. Use Tab 2 to ask from Annual Reports .")
                #st.session_state.messages.append({"role": "assistant", "content": "Please try to improve your question. Note this tab is for financial statement questions. Use Tab 2 to ask from Annual Reports ."})
              
    else:
        query = st.chat_input("Enter your question:")
        st.markdown("""

        I am capable of reviewing the annual reports from 2018 to 2022. Please ask me questions and I will try my level best to provide accurate responses
              
        **Some Sample Questions:**
      
        - What are the operating expenses of the Marvell for last 2 years?
        - What are the risks Marvell is facing?
        
        """)
        
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
import snowflake.connector
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import prompts

st.set_page_config(layout="wide")

# Variables
sf_db = st.secrets["sf_database"]
sf_schema = st.secrets["sf_schema"]
tick_list = ['BRK.A','AAPL','PG','JNJ','MA','MCO','VZ','KO','AXP', 'BAC']
fin_statement_list = ['income_statement','balance_sheet','cash_flow_statement']
year_cutoff = 20 # year cutoff for financial statement plotting

# establish snowpark connection
conn = st.experimental_connection("snowpark")

# Reset the connection before using it if it isn't healthy
try:
    query_test = conn.query('select 1')
except:
    conn.reset()

@st.cache_data
def pull_financials(database, schema, statement, ticker):
    """
    query to pull financial data from snowflake based on database, schema, statement and ticker
    """
    df = conn.query(f"select * from {database}.{schema}.{statement} where ticker = '{ticker}' order by year desc")
    df.columns = [col.lower() for col in df.columns]
    return df

# metrics for kpi cards
@st.cache_data
def kpi_recent(df, metric, periods=2, unit=1000000000):
    """
    filters a financial statement dataframe down to the most recent periods
    df is the financial statement. Metric is the column to be used.
    """
    return df.sort_values('year',ascending=False).head(periods)[metric]/unit

def plot_financials(df, x, y, x_cutoff, title):
    """"
    helper to plot the altair financial charts
    """
    return st.altair_chart(alt.Chart(df.head(x_cutoff)).mark_bar().encode(
        x=x,
        y=y
        ).properties(title=title)
    ) 

# adding this to test out caching
st.cache_data(ttl=86400)
def fs_chain(str_input):
    """
    performs qa capability for a question using sql vector db store
    the prompts.fs_chain is used but with caching
    """
    output = prompts.fs_chain(str_input)
    return output

# adding this to test out caching
st.cache_data(ttl=86400)
def sf_query(str_input):
    """
    performs snowflake query with caching
    """
    data = conn.query(str_input)
    return data

# create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Financial Statement Questions :dollar:", 
    "Financial Data Exploration :chart_with_upwards_trend:",
    "Shareholder Letter Questions :memo:", 
    "Additional Details :notebook:"]
    )

with st.sidebar:
    st.markdown("""
    # Ask the Oracle of Omaha: Using LLMs to Provide a View into the World of Warren Buffett :moneybag:
    This app enables exploration into the World of Warren Buffett, enabling you to ask financial questions regarding his top investments and over 40 years of his shareholder letters.
    This app is powered by Snowflake :snowflake:, Streamlit, OpenAI, Langchain and Pinecone, leveraging Large Language Models (LLMs)

    Tabs:
    ### 1: Financial Statement Questions :dollar:
    Ask financial questions using natural language regarding the investments
    ### 2: Financial Data Exploration :chart_with_upwards_trend:
    Query Snowflake to view financials for various Warren Buffett investments
    ### 3: Shareholder Letter Questions :memo:
    Ask various questions based on Warren Buffett's shareholder letters from 1977 through 2022  

    **Current Available Companies to ask financials about for tabs 1 and 2:**
    1. Apple
    2. Bershire Hathaway
    3. Proctor and Gamble
    4. Johnson and Johnson
    5. Mastercard
    6. Moodys Corp
    7. Verizon
    8. American Express
    9. Bank of America

    Produced by @randypettus
    """)

with tab1:
    st.markdown("""
    # Financial Statement Questions :dollar:
    ### Leverage LLMs to translate natural language questions related to financial statements and turn those into direct Snowflake queries
    Data is stored and queried directly from income statement, balance sheet, and cash flow statement in Snowflake

    **Example questions to ask:**

    - What was Proctor and Gamble's net income from 2010 through 2020?
    - What was Apple's debt to equity ratio for the last 5 years?
    - Rank the companies in descending order based on their net income in 2022. Include the ticker and net income value
    - What has been the average for total assets and total liabilities for each company over the last 3 years? List the top 3
    """
    )
    
    str_input = st.text_input(label='What would you like to answer? (e.g. What was the revenue and net income for Apple for the last 5 years?)')

    if len(str_input) > 1:
        with st.spinner('Looking up your question in Snowflake now...'):
            try:
                output = fs_chain(str_input)
                #st.write(output)
                try:
                    # if the output doesn't work we will try one additional attempt to fix it
                    query_result = sf_query(output['result'])
                    if len(query_result) > 1:
                        st.write(query_result)
                        st.write(output)
                except:
                    st.write("The first attempt didn't pull what you were needing. Trying again...")
                    output = fs_chain(f'You need to fix the code but ONLY produce SQL code output. If the question is complex, consider using one or more CTE. Examine the DDL statements and answer this question: {output}')
                    st.write(sf_query(output['result']))
                    st.write(output)
            except:
                st.write("Please try to improve your question. Note this tab is for financial statement questions. Use Tab 3 to ask from shareholder letters. Also, only a handful of companies are available, which you can see on the side bar.")
                st.write(f"Final errored query used:")
                st.write(output)


with tab3:
    st.markdown("""
    # Shareholder Letter Questions :memo:
    ### Ask questions from all of Warren Buffett's annual shareholder letters dating back to 1977

    These letters are much anticipated by investors for the wealth of knowledge that Buffett provides.
    The tool allows you to interact with these letters by asking questions and a LLM is used to find relevant answers.

    **Example questions to ask:**
    
    - How does your view on managing investment risk differ from professional investment managers?
    - What was your gain in net worth in 1984?
    - What are some of your biggest lessons learned?
    - What do you look for in managers?
    - Are markets efficient? Give a specific example that you have used in a letter.
    """
    )

    query = st.text_input("What would you like to ask Warren Buffett?")
    if len(query)>1:
        with st.spinner('Looking through lots of Shareholder letters now...'):
            
            try:
                st.caption(":blue[Warren's response] :sunglasses:")
                #st.write(prompts.letter_qa(query))
                result = prompts.letter_chain(query)
                st.write(result['result'])
                st.caption(":blue[Source Documents Used] :📄:")
                st.write(result['source_documents'])
            except:
                st.write("Please try to improve your question")

with tab4:
    st.markdown("""
    Additional Details:
    - Tabs 1 and 3 can likely be consolidated leveraging Langchain "tools" with better prompting templates.
    """)
    st.subheader("App Architecture")
    
    from PIL import Image
    image = Image.open('./assets/buffett-app-architecture.png')
    st.image(image, caption='Buffett app architecture')
