from langchain_community.document_loaders import PyPDFLoader

import gradio as gr

import os
import glob
import tiktoken
import pandas as pd
from datetime import datetime
import openai
from openai import AzureOpenAI
from utils import *
from chromadb_utils import *

## Chromadb configuration
import chromadb
chroma_client = chromadb.Client()
collection_name = 'story_collection'


openai.api_key = "<>"

already_stored_cdb = False
collection = None

def init_vector_db_condfig():    
#if not already_stored_cdb:
    # PDF data location/path
    root_directory = 'data'
    chunk_size = 1024
    overlap = 80
    doc_content_df = pd.DataFrame()
    
    # Listing all the pdf files listed in root_directory
    files = get_pdf_files(root_directory)
    
    # Extract the files content and persisting in DF
    for file in files:
        doc_content = extract_pdf_content(file)    
        entry  = {'doc_name':file,'doc_content' : doc_content}
        doc_content_df = doc_content_df.append(entry, ignore_index=True)
    
    # creating the chunks of files content of configured size
    encoding = tiktoken.get_encoding("cl100k_base")
    doc_content_df = doc_content_df.apply(lambda row: create_chunks(row, encoding, chunk_size, overlap), axis=1)
    
    # Creating the chromadb collection. if it already created, will return collection instance with exception - collection already present.
    try:
        collection = chroma_client.get_or_create_collection(name=collection_name)
    except Exception as ex:
        print(f'Collection creation failed with - {ex}')
    
    # Upsert the chunks in chroma db with respective ID's
    doc_content_df = doc_content_df.apply(lambda row: upsert_to_chromadb(row, collection), axis=1)
    
    timestamp = datetime.now().timestamp()
    
    doc_content_df.to_csv(f'data/{collection_name}-{timestamp}.csv')



system_prompt = "You are helpful AI assistant."


def generate_ai_response(context, sys_msg, criteria):

    msgs = [{"role":"system", "content": f'{sys_msg} , context is - {context}'},{"role":"user", "content": f'{criteria}'}]
             
    try:
#         client = AzureOpenAI(
#           azure_endpoint = azure_endpoint,
#           api_key = api_key, 
#           api_version = api_version
#         )
        
#         response = client.chat.completions.create(
#             model = azure_deployment,
#             messages = msgs
#         )
#         respon_content = response.choices[0].message.content

#         return respon_content
    
        chat_completion = openai.chat.completions.create(model="gpt-3.5-turbo", messages=msgs)
        respon_content = chat_completion.choices[0].message.content

        return respon_content

    except Exception as ex:
        print(f"OPENAI Error : - {ex}")
        return "OPENAI_ERROR, Please contact Hughes SDGML Team."


def get_matching_chunk(query):
    
    collection = chroma_client.get_collection(name=collection_name)
    
    results = collection.query(query_texts=[f"{query}"], n_results=1)
    ref_document_name = results.get('ids')[0][0].split('/')[-1]
    chunk_text = results.get('documents')[0][0]
    
    return ref_document_name, chunk_text
    
    

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])

    def respond(message, chat_history):
        ref_document_name, chunk_text = get_matching_chunk(message)
        ai_response = generate_ai_response(chunk_text, system_prompt, message)
        chat_history.append((message, ai_response + f' [Reference Document - {ref_document_name}]'))
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])

if __name__ == "__main__":
    init_vector_db_condfig()
    demo.launch(server_name="0.0.0.0", server_port=4065, debug=False, auth=('Quantum123', 'pass123'), share=True)