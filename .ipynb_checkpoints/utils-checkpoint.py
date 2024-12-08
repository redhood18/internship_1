from langchain_community.document_loaders import PyPDFLoader

import os
import glob
import tiktoken
import pandas as pd


def extract_pdf_content(pdf_path):
    text =  ''
    try:
        loader = PyPDFLoader(pdf_path)
        pages = loader.load_and_split()
        
        for page_number in range(len(pages)):
            #print('text===', page_number)
            #print('text===', pages[page_number].page_content)
            text = text+pages[page_number].page_content
    except Exception as ex:
        print(f'Failed to extract the connect for {pdf_path} document, Excpetion encountered : {ex}')
    
    return text
    


def get_pdf_files(directory):
    # List to store all PDF files
    pdf_files = []
    
    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check the extension of the files
            if file.lower().endswith('.pdf') and not file.startswith('.'):
                # Add the file to the list
                pdf_files.append(os.path.join(root, file))
    
    # Return the list of PDF files
    return pdf_files