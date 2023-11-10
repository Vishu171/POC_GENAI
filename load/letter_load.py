import pinecone
import streamlit as st
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.text_splitter import TokenTextSplitter,RecursiveCharacterTextSplitter,Language
from shareplum import Office365
from shareplum import Site
from shareplum.site import Version
import PyPDF2
from io import BytesIO
import os

#Variables

sp_url = st.secrets["sp_url"]
sp_site_url = st.secrets["sp_site_url"]
sp_file_path = st.secrets["sp_file_path"]
sp_username = st.secrets["sp_username"]
sp_password = st.secrets["sp_password"]
openai_key = st.secrets["openai_key"]
index_name = "knowledgebase"


def connect_sharepoint():
    auth = Office365(sp_url, sp_username, sp_password).GetCookies()
    sites = sp_url + sp_site_url
    site = Site(sites, version=Version.v365, authcookie=auth)
    return site


def get_folder(file_path):
    site = connect_sharepoint()
    folder = site.Folder(file_path)
    return folder


def get_pdf_stream(file_path):
    folder = get_folder(sp_file_path)
    file = folder.get_file(file_path)
    pdf_stream = BytesIO(file)
    return pdf_stream

def operation():
    
    #Initialize Pinecone
    pinecone.init(
        api_key=st.secrets['pinecone_key'],
        environment=st.secrets['pinecone_env']
    )
    
    indexes = pinecone.list_indexes()  # checks if provided index exists
    #if index_name in indexes:
        #pinecone.delete_index(index_name)
        #print("Deleted Index")
        ##st.write("Delete Index")
        #pinecone.create_index(index_name, dimension=1536,
                              #metric="cosine", pods=1, pod_type="p1.x1")
        
    text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0)
    
    # Process PDFs from SharePoint
    pdfs = [file for file in get_folder(sp_file_path).files if file['Name'].endswith('.pdf')]
    page_list = []
    
    for pdf in pdfs:
        pdf_name = pdf['Name']
        pdf_file_path = os.path.join(sp_file_path, pdf_name).replace('\\','/')
        #print (pdf_file_path)
        ##st.write(pdf_file_path)
        pdf_stream = get_pdf_stream(pdf_name)
    
        # Extract text from PDF using PyPDF2
        pdf_reader = PyPDF2.PdfReader(pdf_stream)
        page_text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text += page.extract_text()
        page_list.append(page_text)
    
    flat_list = [item for item in page_list]
    
    text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0)
    #texts = text_splitter.split_documents(flat_list)
    python_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, chunk_size=1000, chunk_overlap=0
    )
    python_docs = python_splitter.create_documents(flat_list)
    python_docs
    
    # Create embeddings and initialize Pinecone
    embeddings = OpenAIEmbeddings(openai_api_key=openai_key)
    docsearch = Pinecone.from_texts([t.page_content for t in python_docs], embeddings, index_name=index_name)
